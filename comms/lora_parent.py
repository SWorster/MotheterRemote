"""
Handles LoRa communications for the main RPi.
"""

import time
import serial
import threading
import os
import configs

# where to store data
rpi_data_path = configs.rpi_data_path

# radio connection
ADDR = configs.R_ADDR
BAUD = configs.R_BAUD

# text encoding
EOL = configs.EOL
EOF = configs.EOF
utf8 = configs.utf8

# timing
long_s = configs.long_s
mid_s = configs.mid_s
short_s = configs.short_s


class Radio:
    """Runs radio on serial"""

    def __init__(self):
        self.data: list[str] = []
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.l = threading.Thread(target=self._listen)  # listener in background
        self.l.daemon = True
        self.l.start()

    def _start_listen(self) -> None:
        """Tries to start listener, if not already running"""
        try:
            self.l.start()
        except RuntimeError:
            p("Listener already running")

    def _listen(self) -> None:
        """Radio listener that runs continuously"""
        while True:
            time.sleep(short_s)  # wait
            full_msg = self.s.read_until(EOF.encode(utf8))  # get message

            if "rsync".encode(utf8) in full_msg:  # if rsync, handle separately
                self._rsync_from_radio(full_msg.decode(utf8))
            else:
                msg_arr = full_msg.decode(utf8).split(EOL)  # decode and split
                for msg in msg_arr:
                    self.data.append(msg)  # put into buffer to be sent

    def _send(self, msg: str | list[str] = "rx") -> None:
        """Sends message to child RPi over radio

        Args:
            msg (str | list[str], optional): message to send. Defaults to "rx".
        """
        if isinstance(msg, list):  # convert to string if needed
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode(utf8))

    def return_collected(self) -> list[str]:
        """Returns all data gathered since last collection

        Returns:
            list[str]: messages to send
        """
        d = self.data[:]  # pass by value, not reference
        self.data.clear()  # clear buffer
        return d

    def send_loop(self) -> None:
        """ui for debugging only"""
        while True:
            i = input("Send: ")
            self._send(i)

    def rpi_to_client(self, m: str) -> None:
        """Sends a message over radio

        Args:
            m (str): message to send
        """
        if m == "rsync":  # filter out rsync requests
            p("Got rsync request.")
            self._send("rsync list")  # ask child for list of dat files
            return
        p(f"Sending to radio: {m}")
        self._send(m)

    def client_to_rpi(self) -> str:
        """Returns messages waiting in buffer

        Returns:
            str: messages to send, concatenated
        """
        msg_arr = self.return_collected()  # get data from buffer
        if len(msg_arr) != 0:  # if there's data to send
            p(f"Received over radio: {msg_arr}")
        return EOL.join(msg_arr)  # return to be sent

    def _rsync_from_radio(self, m: str) -> None:
        """Called when child RPi returns rsync data"""

        if "rsync files" in m:  # got child RPi's file list
            self._compare_files(m)

        elif m.startswith("[rsync files"):  # different format, just in case
            self._compare_files(m)

        else:  # must be file/data to store
            s = m.replace("rsync", "")  # remove trigger
            split = s.index("\n")  # get where first line ends
            name = rpi_data_path + s[:split].strip()  # get name
            s = s[split + 1 :]  # separate rest of fie
            p(f"Saving file at {name}")
            with open(name, "w+") as file:
                file.write(s)

    def _ask_child_for_file(self, filename: str) -> None:
        """Get file from child for rsync

        Args:
            s (str): file name
        """
        p(f"Asking for file {filename}")
        s = f"rsync {filename}"
        self._send(s)

    def _compare_files(self, m: str) -> None:
        """List which files to get from child. If parent (this RPi) doesn't have a file, or has an outdated version, send a request to the child to return the file.

        Args:
            m (str): list of all .dat files from child with last modified date
        """
        # dict of all .dat files from this RPi with dates
        parent = self._get_file_list()
        # get rid of brackets and quotes
        m.replace("[", "").replace("]", "").replace("'", "")
        c1 = m.split(",")  # list of all child .dat files with dates

        c_list = [s.strip() for s in c1]  # strip whitespace

        for i in c_list:  # get rid of rsync header
            if "rsync" in i:
                c_list.remove(i)

        child: dict[str, float] = {}  # format child list as dict
        for i in c_list:
            j = i.split(";")
            child.update({j[0].strip(): float(j[1].strip())})

        for c in child.keys():
            p_date = parent.get(c)
            c_date = child.get(c)
            if c_date == None:  # something must have broken somewhere
                continue
            elif p_date == None:  # no match in parent dict
                p(f"No match for file {c}")
                self._ask_child_for_file(c)  # send request
            elif p_date <= c_date:  # if child file more recent
                p(f"More recent version of {c} found")
                self._ask_child_for_file(c)  # send request

    def _get_file_list(self) -> dict[str, int]:
        """Gets dict of all .dat files in the data directory on this RPi, with the corresponding date of modification

        Returns:
            dict[str, int]: file name and modified date
        """

        def _all_file_list(path: str = os.getcwd()) -> list[str]:
            """Recursively finds all .dat files in the RPi data directory.

            Args:
                path (str, optional): current path to search. Defaults to current working directory.

            Returns:
                list[str]: all .dat files in current directory
            """
            to_return: list[str] = []
            try:
                file_list = os.listdir(path)  # get list of files
            except:
                p(f"Cannot find directory {path}, returning")
                return []  # something went wrong, stop recursing

            for entry in file_list:
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):  # if directory, recurse on it
                    to_return.extend(_all_file_list(fullPath))
                if fullPath.endswith(".dat"):  # if .dat file, add to list
                    to_return.append(fullPath)
            return to_return

        l = _all_file_list(rpi_data_path)
        d: dict[str, int] = {}
        for file in l:
            if file.endswith(".dat"):  # filter for dat files
                ctime = os.path.getctime(file)  # seconds since 1970
                d.update({file: int(ctime)})  # new dict entry for name and date
        return d


def p(s: str) -> None:
    """Flushes buffer and prints. Enables print in threads

    Args:
        s (str): string to print
    """
    print(s, flush=True)


if __name__ == "__main__":
    p("\n\n")
    s = Radio()
    s.send_loop()

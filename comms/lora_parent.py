"""
Handles LoRa communications from main RPi.
"""

import time
import serial
import threading
import os

import configs

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

rpi_data_path = configs.rpi_data_path


class Radio:
    def __init__(self):
        self.data: list[str] = []
        self.s = serial.Serial(ADDR, BAUD, timeout=None)
        self.l = threading.Thread(target=self._listen)  # listener in background
        self.l.daemon = True
        self.l.start()

    def _start_listen(self) -> None:
        """tries to start listener, if not already running"""
        try:
            self.l.start()
        except RuntimeError:
            print("Listener already running")

    def _listen(self) -> None:
        """radio listener that runs continuously"""
        self.live = True
        while self.live:
            time.sleep(short_s)
            full_msg = self.s.read_until(EOF.encode(utf8))
            msg_arr = full_msg.decode(utf8).split(EOL)
            for msg in msg_arr:
                print(f"Received over radio: {msg}")
                if "rsync" in msg:
                    self._rsync_from_radio(msg)
                self.data.append(msg)

    def _send(self, msg: str | list[str] = "rx") -> None:
        """sends message to child rpi over radio

        Args:
            msg (str | list[str], optional): message to send. Defaults to "rx".
        """
        if isinstance(msg, list):
            m = EOL.join(msg)
        else:
            m = msg
        self.s.write((m + EOF).encode(utf8))

    def return_collected(self) -> list[str]:
        d = self.data[:]  # pass by value, not reference
        self.data.clear()
        return d

    def send_loop(self) -> None:
        """ui for debugging only"""
        while True:
            i = input("Send: ")
            self._send(i)

    def rpi_to_client(self, m: str) -> None:
        """sends a message over radio

        Args:
            m (str): message to send
        """
        if m == "rsync":  # filter out rsync requests
            print("Got rsync request!")
            self._send("rsync list")  # ask child for list of dat files
            return
        print(f"Sending to radio: {m}")
        self._send(m)

    def client_to_rpi(self) -> str:
        """returns messages waiting in buffer

        Returns:
            str: messages to send, concatenated
        """
        msg_arr = self.return_collected()
        if len(msg_arr) != 0:
            print(f"Received over radio: {msg_arr}")
        return EOL.join(msg_arr)

    def _rsync_from_radio(self, m: str) -> None:
        """called when child rpi returns rsync data"""
        if m.startswith("rsync files"):
            self._compare_files(m)

    def _ask_child_for_file(self, filename: str) -> None:
        """get file from child for rsync

        Args:
            s (str): file name
        """
        print(f"Rsync: asking for file {filename}")
        s = f"rsync {filename}"
        self._send(s)

    def _compare_files(self, m: str) -> None:
        """List which files to get from child. If parent (this rpi) doesn't have a file, or has an outdated version, send a request to the child to return the file.

        Args:
            m (str): list of all .dat files from child with last modified date
        """
        parent = (
            self._get_file_list()
        )  # dict of all .dat files from this rpi with dates
        c_list = m.split(EOL)  # list of all child .dat files with dates
        c_list.remove("rsync files")  # remove header

        child: dict[str, int] = {}  # format child list as dict
        for i in child:
            j = i.split(",")
            child.update({j[0]: int(j[1])})

        for c in child.keys():
            p_date = parent.get(c)
            c_date = child.get(c)
            if c_date == None:  # something must have broken somewhere
                continue
            elif p_date == None:  # no match in parent dict
                self._ask_child_for_file(c)  # send request
            elif p_date <= c_date:  # if child file more recent
                self._ask_child_for_file(c)  # send request

    def _get_file_list(self) -> dict[str, int]:
        """gets dict of all .dat files in the data directory on this rpi, with the corresponding date of modification

        Returns:
            dict[str, int]: file name and modified date
        """

        def _all_file_list(path: str = os.getcwd()) -> list[str]:
            """recursively finds all .dat files in the rpi data directory.

            Args:
                path (str, optional): current path to search. Defaults to current working directory.

            Returns:
                list[str]: all .dat files in current directory
            """
            file_list = os.listdir(path)
            for entry in file_list:
                fullPath = os.path.join(path, entry)
                if os.path.isdir(fullPath):  # recurse on directory
                    file_list.extend(_all_file_list(fullPath))
            return file_list

        l = _all_file_list(rpi_data_path)
        d: dict[str, int] = {}
        for file in l:
            if file.endswith(".dat"):  # filter for dat files
                ctime = os.path.getctime(file)  # seconds since 1970
                d.update({file: int(ctime)})  # new dict entry for name and date
        return d


if __name__ == "__main__":
    s = Radio()
    s.send_loop()


# def getListOfFiles(path: str = "") -> list[str]:
#     listOfFile = os.listdir(path)
#     nameList = listOfFile
#     allFiles: dict[str, tuple[int, int]]
#     for entry in listOfFile:
#         fullPath = os.path.join(path, entry)
#         if os.path.isdir(fullPath):
#             x = getListOfFiles(fullPath)
#             nameList.extend(x)
#         else:
#             print("getting size of fullPath: " + fullPath)
#             size = os.path.getsize(fullPath)
#             ctime = os.path.getctime(fullPath)
#             item = (fullPath, size, ctime)
#             allFiles.append(item)
#     return allFiles

# # set with elements in child that aren't in parent
# child_unique = set(child)
# child_unique.difference_update(parent)
# p_dict: dict[str, int] = {}
# for i in parent:
#     j = i.split(",")
#     p_dict.update({j[0]: int(j[1])})

# for c in child_unique:
#     t = c.split(",")
#     p_date = p_dict.get(t[0])
#     if p_date == None:
#         continue
#     if int(t[1]) <= p_date:
#         continue
#     ask_child_for_file(t[0])

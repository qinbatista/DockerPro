import time


class Time:

    @classmethod
    def time_stamp(cls):
        return int(time.time())

    @classmethod
    def timestamp_to_date(cls, time_stamp, format_string="%Y-%m-%d %H:%M:%S"):
        time_array = time.localtime(time_stamp)
        format_time = time.strftime(format_string, time_array)
        return str(format_time)

    @classmethod
    def local_format_time(cls, format_string="%Y-%m-%d %H:%M:%S"):
        return cls.timestamp_to_date(int(time.time()),format_string)

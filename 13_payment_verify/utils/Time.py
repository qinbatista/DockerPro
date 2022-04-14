import time


class Time:

    format_string = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def timestamp_to_date(cls, time_stamp, format_string=format_string):
        time_array = time.localtime(time_stamp)
        format_time = time.strftime(format_string, time_array)
        return format_time

    @classmethod
    def local_format_time(cls, format_string=format_string):
        return cls.timestamp_to_date(int(time.time()), format_string)

    @classmethod
    def cmp(cls, first_time, second_time, format_string=format_string):
        first_time = time.strptime(first_time, format_string)
        second_time = time.strptime(second_time, format_string)
        return first_time > second_time

    @classmethod
    def is_valid(cls, date):
        try:
            time.strptime(date, cls.format_string) if ":" in date else time.strptime(date, "%Y-%m-%d")
        except:
            return False
        return True



if __name__ == '__main__':
    result = Time.cmp(
        Time.local_format_time(),
        "2020-11-10 07:48:28",
    )
    print(result)

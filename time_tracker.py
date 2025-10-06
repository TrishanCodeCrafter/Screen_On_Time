import time

class TimeTracker:
    def __init__(self):
        self.start_time = None
        self.total_time = 0
        self.last_60_sot_record = []

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time:
            self.total_time += time.time() - self.start_time
            self.start_time = None

    def reset(self):
        self.start_time = None
        self.total_time = 0

    def get_total_time(self, formatting=False):
        
        if formatting:
            return self.time_formatting(self.total_time + (time.time() - self.start_time) if self.start_time else self.total_time)
            
        if self.start_time:
                return self.total_time + (time.time() - self.start_time)
        return self.total_time

    def time_formatting(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02}:{minutes:02}:{secs:02}"
    
    def sot_estimate(self, current_battery_level, start_battery_level):
        battery_used = start_battery_level - current_battery_level
        sot_so_far = self.get_total_time()
        
        # Maintain a record of the last 60 SOT estimates
        last_60_sot_record = self.last_60_sot_record
        
        if battery_used <= 0:
            last_60_sot_record.clear()
            return "Calculating..."
        
        # Pretty straightforward moving average calculation
        if len(last_60_sot_record) < 60:
            last_60_sot_record.append((sot_so_far / battery_used) * 100)
        else:
            last_60_sot_record.pop(0)
            last_60_sot_record.append((sot_so_far / battery_used) * 100)
        avg_sot_last_60 = sum(last_60_sot_record) / len(last_60_sot_record)
        
        return self.time_formatting(avg_sot_last_60)
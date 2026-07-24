===========================================================
# modules/habits/models.py
streak_count   → Abhi kitne din consecutively
                  kiya hai
                  (ek din bhi miss → reset to 0!)

longest_streak → Sabse lamba streak jo kabhi tha
                  (motivational — "tune 15 din
                   ka streak banaya tha!")

Example:
Jan 1  ✅  streak_count = 1
Jan 2  ✅  streak_count = 2
Jan 3  ✅  streak_count = 3, longest_streak = 3
Jan 4  ❌  streak_count = 0  ← Reset!
           longest_streak = 3  ← Nahi badhta
Jan 5  ✅  streak_count = 1

log_date = Column(Date, nullable=False)
- sirf Date store karta hai (time nhi)
- reason? 1 din me 1 hi log hona chahiye

Jan 15 → completed = True
Jan 16 → completed = False, skip_reason = "tired"

Agar time bhi rakhte → same din 2 baar log
ho sakta tha (bug!) 
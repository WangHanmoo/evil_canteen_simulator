import time, random
from math import floor

GAME_VALUES = {
    "evil_max": 10,
    "complaint_per_warning": 3,
    "warnings_max": 3,
    "base_time_s": 480,
    "min_time_s": 180,
    "max_time_s": 600,
    "bribe_cost": 500,
    "base_income": 100,
    "high_price_bonus": 50,
    "complaint_penalty_money": -50,
    "inspection_bribe_window_s": 10,
    "idle_no_evil_gain_time_s": 60,
    "idle_reward_time_s": 30,
    "evil_time_penalty_per_3": 60,
}

CUSTOMER_TYPES = {
    "normal": {"complaint_modifier": 0.0},
    "picky": {"complaint_modifier": 0.2},
    "careless": {"complaint_modifier": -0.3},
    "irritable": {"complaint_modifier": 0.35},
}

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class GameplayState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.evil = 0
        self.money = 1000
        self.satisfaction = 100
        self.complaints = 0
        self.warnings = 0
        self.time_remaining = GAME_VALUES["base_time_s"]
        self.normal_ingredients = 10
        self.inspector_active = False
        self.inspector_timer = 0.0
        self.last_evil_action_time = None
        self.idle_added_flag = False
        self.evil_time_penalty_applied_for = 0
        self.game_over = False
        self.ending_reason = None

    def _roll_complaint(self, base_prob):
        cust = random.choices(list(CUSTOMER_TYPES.keys()), weights=[0.5,0.15,0.2,0.15])[0]
        mod = CUSTOMER_TYPES[cust]["complaint_modifier"]
        satisf_penalty = 0.2 if self.satisfaction < 50 else 0.0
        prob = clamp(base_prob + mod + satisf_penalty, 0.0, 0.95)
        return random.random() < prob, prob, cust

    def _apply_evil_delta(self, d):
        prev = self.evil
        self.evil = clamp(self.evil + d, 0, GAME_VALUES["evil_max"])
        self.last_evil_action_time = time.time()
        self.idle_added_flag = False
        groups_now = self.evil // 3
        if groups_now > self.evil_time_penalty_applied_for:
            to_apply = groups_now - self.evil_time_penalty_applied_for
            self.time_remaining -= to_apply * GAME_VALUES["evil_time_penalty_per_3"]
            self.evil_time_penalty_applied_for = groups_now
            self.time_remaining = clamp(self.time_remaining, GAME_VALUES["min_time_s"], GAME_VALUES["max_time_s"])

    def _register_complaint(self):
        self.complaints += 1
        if self.complaints >= GAME_VALUES["complaint_per_warning"]:
            self.complaints = 0
            self._register_warning()

    def _register_warning(self):
        self.warnings += 1
        if self.warnings >= GAME_VALUES["warnings_max"]:
            self.game_over = True
            self.ending_reason = "closed_by_regulator"

    def _spawn_inspector(self):
        self.inspector_active = True
        self.inspector_timer = GAME_VALUES["inspection_bribe_window_s"]

    def _dismiss_inspector(self, bribed=False):
        self.inspector_active = False
        self.inspector_timer = 0.0
        if not bribed:
            self._register_warning()

    # public actions:
    def serve_normal(self):
        """Serve normally (prefer normal ingredient)."""
        if self.normal_ingredients > 0:
            self.normal_ingredients -= 1
            complained, prob, cust = self._roll_complaint(0.10)
            if complained:
                self._register_complaint()
                self.money += GAME_VALUES["complaint_penalty_money"]
                return {"msg":"Complaint", "complaint":True, "prob":prob, "cust":cust}
            else:
                self.money += GAME_VALUES["base_income"]
                return {"msg":"Served normally", "income":GAME_VALUES["base_income"]}
        else:
            # forced expired
            return self.use_expired()

    def use_expired(self):
        self._apply_evil_delta(1)
        complained, prob, cust = self._roll_complaint(0.30)
        if complained:
            self._register_complaint()
            self.money += GAME_VALUES["complaint_penalty_money"]
            return {"msg":"Used expired -> complaint", "complaint":True, "prob":prob, "cust":cust}
        else:
            self.money += GAME_VALUES["base_income"]
            return {"msg":"Used expired (no complaint)", "income":GAME_VALUES["base_income"]}

    def skimp(self):
        self._apply_evil_delta(1)
        self.satisfaction = clamp(self.satisfaction - 20, 0, 100)
        complained, prob, cust = self._roll_complaint(0.20)
        if complained:
            self._register_complaint()
            self.money += GAME_VALUES["complaint_penalty_money"]
            return {"msg":"Skimp -> complaint", "complaint":True, "prob":prob, "cust":cust}
        else:
            income = int(GAME_VALUES["base_income"] * 0.9)
            self.money += income
            return {"msg":"Skimp sold", "income":income}

    def price_hike(self):
        self._apply_evil_delta(1)
        refused = (random.random() < 0.20)
        if refused:
            return {"msg":"Customers refused to pay", "refused":True}
        else:
            self.money += GAME_VALUES["base_income"] + GAME_VALUES["high_price_bonus"]
            complained, prob, cust = self._roll_complaint(0.15)
            if complained:
                self._register_complaint()
                return {"msg":"Price hike sold but complaint", "complaint":True}
            return {"msg":"Price hike sold", "income": GAME_VALUES["base_income"] + GAME_VALUES["high_price_bonus"]}

    def dirty_dishes(self):
        self._apply_evil_delta(1)
        self.satisfaction = clamp(self.satisfaction - 30, 0, 100)
        complained, prob, cust = self._roll_complaint(0.50)
        if complained:
            self._register_complaint()
            self.money += GAME_VALUES["complaint_penalty_money"]
            return {"msg":"Dirty dishes complaint", "complaint":True}
        else:
            self.money += GAME_VALUES["base_income"]
            return {"msg":"Dirty dishes served (no complaint)"}

    def kick_customer(self):
        self._apply_evil_delta(2)
        self._register_warning()
        return {"msg":"Kicked customer -> immediate warning", "warning":True}

    def bribe_inspector(self):
        if self.inspector_active:
            if self.money >= GAME_VALUES["bribe_cost"]:
                self.money -= GAME_VALUES["bribe_cost"]
                self._dismiss_inspector(bribed=True)
                return {"msg":"Bribe paid", "bribed":True}
            else:
                return {"msg":"Not enough money to bribe", "bribed":False}
        else:
            return {"msg":"No inspector present"}

    def update(self, dt):
        if self.game_over:
            return
        self.time_remaining -= dt
        # idle reward
        now = time.time()
        if self.last_evil_action_time:
            if (now - self.last_evil_action_time) >= GAME_VALUES["idle_no_evil_gain_time_s"] and not self.idle_added_flag:
                self.time_remaining += GAME_VALUES["idle_reward_time_s"]
                self.time_remaining = clamp(self.time_remaining, GAME_VALUES["min_time_s"], GAME_VALUES["max_time_s"])
                self.idle_added_flag = True

        # inspector timer
        if self.inspector_active:
            self.inspector_timer -= dt
            if self.inspector_timer <= 0:
                self._dismiss_inspector(False)

        # spawn check approx every 8-12s
        if not hasattr(self, "_spawn_timer"):
            self._spawn_timer = random.uniform(8.0, 12.0)
        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._spawn_timer = random.uniform(8.0, 12.0)
            if self.evil >= 6:
                if random.random() < 0.5:
                    self._spawn_inspector()

        # end conditions
        if self.evil >= GAME_VALUES["evil_max"]:
            self.game_over = True
            self.ending_reason = "ultimate_runaway"
        if self.time_remaining <= 0 and not self.game_over:
            self.game_over = True
            self.ending_reason = "time_expired"
        if self.warnings >= GAME_VALUES["warnings_max"]:
            self.game_over = True
            self.ending_reason = "closed_by_regulator"

    def evaluate_ending(self):
        if self.ending_reason == "ultimate_runaway":
            return ("King of Greed", "You packed up the loot and ran.")
        if self.ending_reason == "closed_by_regulator":
            return ("Closed by Regulator", "Too many warnings; closure.")
        # time expired - evaluate by evil
        if self.evil <= 3:
            return ("Merciful Vendor", "Low evil. Played safe.")
        elif 4 <= self.evil <= 7:
            return ("Cunning Merchant", "Balanced greed and caution.")
        else:
            return ("King of Greed", "High evil; maximum score.")

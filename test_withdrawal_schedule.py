import sys
from withdrawal_rsu_401K import compute_withdrawal_schedule_single_asset, GROWTH_RATE
from datetime import datetime

def test_compute_withdrawal_schedule_single_asset():
    total_amount_today = 1600000
    start_year = 2026
    end_year = 2030
    schedule = compute_withdrawal_schedule_single_asset(
        total_amount_today, start_year, end_year)
    print(f"Withdrawal schedule for ${total_amount_today:,.0f} from {start_year} to {end_year}:")
    # Basic checks
    assert len(schedule) == (end_year - start_year + 1), "Schedule length mismatch"
    assert all(a > 0 for a in schedule), "All withdrawals should be positive"
    print("Test passed!")
    
    asset = total_amount_today
    current_year = datetime.now().year
    # Grow asset to start_year
    years_to_grow = start_year - current_year
    if years_to_grow > 0:
        asset = asset * (1 + GROWTH_RATE) ** years_to_grow
        print(f"Asset grown from {current_year} to {start_year}: ${asset:,.2f}")

    # simulate the widthdrawal 
    for i, withdrawal in enumerate(schedule):
        year = start_year + i
        beginning = asset
        asset -= withdrawal
        if i < len(schedule) - 1:  # Only grow if not the last year
            asset = asset * (1 + GROWTH_RATE)
        ending = asset
        print(f"Year {year}: Begin=${beginning:,.2f}, Withdraw=${withdrawal:,.2f}, End=${ending:,.2f}")


if __name__ == "__main__":
    test_compute_withdrawal_schedule_single_asset() 
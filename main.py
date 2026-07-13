import flet as ft
from datetime import datetime
import json
import asyncio
import os

async def main(page: ft.Page):
    page.title = "Health Tracker"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = "adaptive"
    
    # UI Inputs
    steps_input = ft.TextField(label="Steps Walked", keyboard_type=ft.KeyboardType.NUMBER)
    water_input = ft.TextField(label="Water Intake (ml)", keyboard_type=ft.KeyboardType.NUMBER)
    sleep_input = ft.TextField(label="Sleep Duration (hours)", keyboard_type=ft.KeyboardType.NUMBER)
    
    # UI History Elements
    history_column = ft.Column(spacing=10)
    avg_text = ft.Text(value="No data logged yet.", size=16, weight=ft.FontWeight.BOLD)

    async def load_data_and_averages(e=None):
        saved_json = await page.shared_preferences.get("daily_logs")
        if saved_json is not None:
            try:
                logs = json.loads(saved_json)
            except Exception:
                logs = {}
        else:
            logs = {}
        
        history_column.controls.clear()
        
        if not logs:
            avg_text.value = "No data logged yet."
            page.update()
            return
            
        sorted_dates = sorted(logs.keys(), reverse=True)[:7]
        total_steps = total_water = total_sleep = 0
        
        for date in sorted_dates:
            day_data = logs[date]
            steps = day_data.get("steps", 0)
            water = day_data.get("water", 0)
            sleep = day_data.get("sleep", 0.0)
            
            total_steps += steps
            total_water += water
            total_sleep += sleep
            
            history_column.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(f"Date: {date}", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Steps: {steps:,} | Water: {water}ml | Sleep: {sleep} hrs")
                        ]),
                        padding=10
                    )
                )
            )
            
        days_count = len(sorted_dates)
        avg_steps = int(total_steps / days_count)
        avg_water = int(total_water / days_count)
        avg_sleep = round(total_sleep / days_count, 1)
        
        avg_text.value = f"7-Day Averages:\nSteps: {avg_steps:,} | Water: {avg_water}ml | Sleep: {avg_sleep} hrs"
        page.update()

    async def save_clicked(e):
        try:
            steps = int(steps_input.value) if steps_input.value else 0
            water = int(water_input.value) if water_input.value else 0
            sleep = float(sleep_input.value) if sleep_input.value else 0.0
            if steps < 0 or water < 0 or sleep < 0:
                raise ValueError
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter positive numbers."))
            page.snack_bar.open = True
            page.update()
            return

        saved_json = await page.shared_preferences.get("daily_logs")
        logs = json.loads(saved_json) if saved_json else {}
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        logs[today_str] = {"steps": steps, "water": water, "sleep": sleep}
        
        await page.shared_preferences.set("daily_logs", json.dumps(logs))
        
        steps_input.value = ""
        water_input.value = ""
        sleep_input.value = ""
        
        page.snack_bar = ft.SnackBar(ft.Text("Metrics saved successfully!"))
        page.snack_bar.open = True
        
        await load_data_and_averages()

    page.add(
        ft.Text("Log Today's Metrics", size=24, weight=ft.FontWeight.BOLD),
        steps_input,
        water_input,
        sleep_input,
        ft.ElevatedButton("Save Entry", on_click=save_clicked),
        ft.Divider(),
        ft.Text("Weekly Summary", size=20, weight=ft.FontWeight.BOLD),
        avg_text,
        ft.Divider(),
        ft.Text("Recent History", size=20, weight=ft.FontWeight.BOLD),
        history_column
    )
    
    await asyncio.sleep(0.5)
    await load_data_and_averages()

# Production configuration targeting the Render web server port environment
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    ft.app(target=main, port=port, view=None)
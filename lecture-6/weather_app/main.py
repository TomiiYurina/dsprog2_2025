import flet as ft
import requests
import db_manager

def main(page: ft.Page):
    db_manager.init_db()
    weather_dict = {
            "101": "晴れ時々曇り", "102": "晴れ時々雨", "103": "晴れ時々雪",
            "110": "晴れのち曇り", "111": "晴れのち雨", "112": "晴れのち雪",
            "201": "曇り時々晴れ", "202": "曇り時々雨", "203": "曇り時々雪",
            "210": "曇りのち晴れ", "211": "曇りのち雨", "212": "曇りのち雪",
            "301": "雨時々晴れ", "302": "雨時々曇り", "311": "雨のち晴れ", "312": "雨のち雪"
        }
    weather_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    area_list = ft.ListView(expand=True, spacing=10)

    # 日付を選択したあとの処理
    def on_date_change(e):
        selected_date = date_picker.value.strftime("%Y-%m-%d")
        # 選択された日付でDBを検索して表示する関数を呼び出す
        display_history_weather(selected_date)

    # カレンダー本体の定義
    date_picker = ft.DatePicker(
        on_change=on_date_change,
    )
    page.overlay.append(date_picker)

    def display_weather_action(e, area_code):
        page.current_area_code = area_code # 今の地域を保存しておく
        weather_display.controls.clear()
        weather_display.controls.append(ft.Text("読み込み中...", size=20))
        page.update()
        try:
            weather_cards = get_weather_report(area_code)
            weather_display.controls.clear()
            weather_display.controls.append(ft.Text(f"地域コード {area_code} の予報", size=20, weight="bold"))
            weather_display.controls.append(weather_cards)
        except Exception as ex:
            weather_display.controls.clear()
            weather_display.controls.append(ft.Text(f"この地域は現在データがありません"))
        page.update()

    def get_weather_report(area_code):
        url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
        res = requests.get(url)
        if res.status_code != 200:
            raise Exception("No Data")
        
        data = res.json()
        report = data[1]
        times = report["timeSeries"][0]["timeDefines"]
        area_data = report["timeSeries"][0]["areas"][0]
        weather_codes = area_data.get("weatherCodes", [])
        
        try:
            temp_area = report["timeSeries"][1]["areas"][0]
            max_temps = temp_area.get("tempsMax", [])
            min_temps = temp_area.get("tempsMin", [])
        except:
            max_temps = []; min_temps = []

        # DBにデータを保存する
        db_manager.save_weather_to_db(area_code, times, weather_codes, max_temps, min_temps)
        # DBからデータを取得する
        db_rows = db_manager.fetch_weather_from_db(area_code)

        
        weather_cards = ft.Row(wrap=True, spacing=20)
        for row in db_rows:
            # DBにある4つのデータを正しく受け取る
            t_val = row[0]  # 日付
            w_code = row[1] # 天気コード
            mx = row[2]     # 最高気温
            mn = row[3]     # 最低気温
            
            # 言葉を辞書から取得
            weather_text = weather_dict.get(w_code, "不明")

            # 基本のアイコン設定する
            if w_code.startswith("1"):
                if weather_text == "不明": weather_text = "晴れ"
                icon_names = [ft.Icons.WB_SUNNY]; icon_colors = [ft.Colors.ORANGE]
            elif w_code.startswith("2"):
                if weather_text == "不明": weather_text = "曇り"
                icon_names = [ft.Icons.CLOUD]; icon_colors = [ft.Colors.GREY_400]
            elif w_code.startswith("3"):
                if weather_text == "不明": weather_text = "雨"
                icon_names = [ft.Icons.UMBRELLA]; icon_colors = [ft.Colors.BLUE_400]
            elif w_code.startswith("4"):
                if weather_text == "不明": weather_text = "雪"
                icon_names = [ft.Icons.AC_UNIT]; icon_colors = [ft.Colors.LIGHT_BLUE_200]

            # 複合アイコンの設定をする
            if w_code in ["101", "110"]:
                icon_names = [ft.Icons.WB_SUNNY, ft.Icons.CLOUD]
                icon_colors = [ft.Colors.ORANGE, ft.Colors.GREY_400]
            elif w_code in ["102", "111"]:
                icon_names = [ft.Icons.WB_SUNNY, ft.Icons.UMBRELLA]
                icon_colors = [ft.Colors.ORANGE, ft.Colors.BLUE_400]
            elif w_code in ["201", "210"]:
                icon_names = [ft.Icons.CLOUD, ft.Icons.WB_SUNNY]
                icon_colors = [ft.Colors.GREY_400, ft.Colors.ORANGE]
            elif w_code in ["202", "211"]:
                icon_names = [ft.Icons.CLOUD, ft.Icons.UMBRELLA]
                icon_colors = [ft.Colors.GREY_400, ft.Colors.BLUE_400]
            elif w_code in ["301", "311"]:
                icon_names = [ft.Icons.UMBRELLA, ft.Icons.WB_SUNNY]
                icon_colors = [ft.Colors.BLUE_400, ft.Colors.ORANGE]
            elif w_code == "302":
                icon_names = [ft.Icons.UMBRELLA, ft.Icons.CLOUD]
                icon_colors = [ft.Colors.BLUE_400, ft.Colors.GREY_400]
            
            # 3. 雷の追加
            if "8" in w_code:
                icon_names.append(ft.Icons.BOLT)
                icon_colors.append(ft.Colors.AMBER_ACCENT_400)

            # カードのデザインを作成
            card = ft.Card(
                elevation=5,
                content=ft.Container(
                    bgcolor=ft.Colors.WHITE, border_radius=20, padding=20, width=160,
                    content=ft.Column([
                        ft.Text(value=t_val[:10], weight="bold"),
                        # アイコンを並べて表示する部分
                        ft.Row(
                            [ft.Icon(name=n, color=c, size=30) for n, c in zip(icon_names, icon_colors)],
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        ft.Text(value=weather_text, size=12, text_align=ft.TextAlign.CENTER),
                        ft.Row([
                            ft.Text(f"{mx}℃", color=ft.Colors.RED_400, weight="bold"),
                            ft.Text("/"),
                            ft.Text(f"{mn}℃", color=ft.Colors.BLUE_400, weight="bold"),
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                )
            )
            weather_cards.controls.append(card)
        return weather_cards
    
    # 選択した日付のデータをDBから探して表示する
    def display_history_weather(target_date):
        area_code = getattr(page, "current_area_code", None)
        if not area_code:
            return

        row = db_manager.fetch_weather_by_date(area_code, target_date)
        
        weather_display.controls.clear()
        weather_display.controls.append(ft.Text(f"{target_date} の記録", size=20, weight="bold"))
        
        if row:
            # rowの中身は (日付, コード, 最高, 最低) の4つタプル
            t_val = row[0]
            w_code = row[1]
            mx = row[2]
            mn = row[3]
            
            # ここでも辞書を使って言葉を出す
            weather_text = weather_dict.get(w_code, "不明")
            
            # 表示する
            weather_display.controls.append(
                ft.Text(f"天気: {weather_text} ({w_code}), 気温: {mx}℃/{mn}℃")
            )
        else:
            weather_display.controls.append(ft.Text("その日のデータはDBに残っていません。"))
        page.update()

    def load_areas():
        url = "http://www.jma.go.jp/bosai/common/const/area.json"
        res = requests.get(url)
        data = res.json()
        offices = data["offices"]

        regions = {
            "北海道地方": ["011000","012000","013000","014030","015000","016000","017000"],
            "東北地方": ["020000","030000","040000","050000","060000","070000"],
            "関東地方": ["080000", "090000", "100000", "110000", "120000", "130000", "140000"],
            "中部地方": ["150000", "160000", "170000", "180000", "190000", "200000", "210000", "220000","230000"],
            "近畿地方": ["240000", "250000", "260000", "270000", "280000", "290000","300000"],
            "中国地方": ["310000", "320000", "330000", "340000","350000"],
            "四国地方": ["360000", "370000", "380000", "390000"],
            "九州・沖縄": ["400000","410000", "420000", "430000", "440000", "450000", "460040","460100","471000"]
        }

        area_list.controls.clear()
        for region_name, codes in regions.items():
            for code in codes:
                area_name = offices.get(code, {}).get("name", "不明")
                # DBに保存（または更新）する
                db_manager.save_area_info(code, area_name, region_name)

        # DBから全エリア情報を取得する
        db_areas = db_manager.fetch_all_areas()
        area_list.controls.clear()

        # 地方ごとにまとめ直すために、一時的な辞書を作る
        display_data = {}
        for code, a_name, r_name in db_areas:
            if r_name not in display_data:
                display_data[r_name] = []
            display_data[r_name].append((code, a_name))

        # DBから作った display_data を使って ExpansionTile を作る
        for r_name, area_info_list in display_data.items():
            tile = ft.ExpansionTile(title=ft.Text(r_name, weight="bold"), controls=[])
            for code, a_name in area_info_list:
                tile.controls.append(
                    ft.ListTile(
                        title=ft.Text(a_name), 
                        on_click=lambda e, c=code: display_weather_action(e, c)
                    )
                )
            area_list.controls.append(tile)
        page.update()


    page.appbar = ft.AppBar(
        title=ft.Text("天気予報", color=ft.Colors.WHITE),
        bgcolor=ft.Colors.DEEP_PURPLE_700,
        leading=ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color=ft.Colors.WHITE),
    )
    history_button = ft.ElevatedButton(
        "過去の予報を検索",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=lambda _: setattr(date_picker, "open", True) or page.update(),
    )
    page.add(
        ft.Row([
            ft.Container(
                content=ft.Column([ft.Text("地域を選択", size=20, weight="bold"), area_list]), 
                width=300, padding=10
            ),
            ft.VerticalDivider(),
            ft.Column([
                history_button, 
                weather_display
            ], expand=True)
        ], expand=True)
        
    )

    load_areas()

ft.app(target=main)
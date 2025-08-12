from utils.useful_functions import write_number
from components import MyButton, MyIconButton, MyMiniIcon, ColoredIcon, ColoredButton, BoxStudentNote
from services.supabase_client import school_republic_fr, national_devise_fr, school_delegation_fr, school_name_fr
from utils.styles import *
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, openpyxl, uuid
import pandas as pd
import io, requests, uuid
from services.async_functions.report_book_functions import *
from utils.useful_functions import add_separator, get_rating
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

DOCUMENTS_BUCKET = 'documents'


class ReportBook(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True
        )

        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # Kpi...
        self.nb_success = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)
        self.nb_fails = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)
        self.success_rate = ft.Text('-', size=28, font_family='PPM', weight=ft.FontWeight.BOLD)

        self.ct_success = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['nb > 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_success,
                            ft.Text(languages[lang]['success 2'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_fails = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'teal', 'teal50'),
                            ft.Text(languages[lang]['nb < 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_fails,
                            ft.Text(languages[lang]['fails'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_rate = ft.Container(
            width=170, height=120, padding=10, border_radius=24, border=ft.border.all(1, 'white'),
            bgcolor='white',
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'deeporange', 'deeporange50'),
                            ft.Text(languages[lang]['rate > 10'].upper(), size=12,
                                    font_family='PPI',
                                    color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.success_rate,
                            ft.Text(languages[lang]['success rate'], size=11, font_family='PPI',
                                    color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # Main window...
        self.search = ft.TextField(
            **cool_style, width=250, prefix_icon=ft.Icons.SEARCH, on_change=self.on_search_change
        )
        self.table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['name'], languages[lang]['class'], languages[lang]['sequence'],
                    languages[lang]['points'], languages[lang]['coefficient'], languages[lang]['average'],
                    languages[lang]['status'], languages[lang]['rank'], 'Actions'
                ]
            ]
        )
        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                controls=[
                    # kpi...
                    ft.Row(
                        controls=[
                            self.ct_success, ft.VerticalDivider(),
                            self.ct_fails, ft.VerticalDivider(),
                            self.ct_rate
                        ]
                    ),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                bgcolor='white', border_radius=16, padding=0, expand=True,
                                content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=20,
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[lang]['quarterly reports'],
                                                                ft.Icons.FOLDER_OPEN,
                                                                None
                                                            ),
                                                            ColoredButton(
                                                                languages[lang]['annual reports'], ft.Icons.FOLDER_OPEN,
                                                                None
                                                            )
                                                        ]
                                                    ),
                                                    self.search
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=20,
                                            content=ft.Row(
                                                controls=[
                                                    ft.Row(
                                                        controls=[
                                                            ft.Icon(
                                                                ft.Icons.DOWNLOAD_DONE, size=20, color="black87"
                                                            ),
                                                            ft.Text(languages[lang]['data extraction'].upper(), size=12,
                                                                    font_family='PPB'),
                                                        ]
                                                    ),
                                                    ft.Row(
                                                        controls=[
                                                            ColoredButton(
                                                                languages[lang]['pdf format'],
                                                                ft.Icons.PICTURE_AS_PDF_SHARP,
                                                                None
                                                            ),
                                                            ColoredButton(
                                                                languages[lang]['xls format'],
                                                                ft.Icons.FILE_PRESENT,
                                                                None
                                                            )
                                                        ]
                                                    )
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        )

        # details window...
        self.det_table = ft.DataTable(
            **datatable_style, columns=[
                ft.DataColumn(ft.Text(option)) for option in [
                    languages[lang]['subject'], languages[lang]['note'], languages[lang]['coefficient'],
                    languages[lang]['total'], languages[lang]['rating'],
                ]
            ]
        )
        self.det_name = ft.Text('-', size=16, font_family='PPB')
        self.det_surname = ft.Text('-', size=12, color='grey', font_family='PPM')
        self.det_image = ft.CircleAvatar(radius=30)
        self.det_bg = ft.CircleAvatar(radius=33, bgcolor=BASE_COLOR)
        self.det_zone = ft.Stack(
            alignment=ft.alignment.center, controls=[self.det_bg, self.det_image]
        )
        self.det_sequence = ft.Text(size=16, font_family="PPM")
        self.det_class = ft.Text(size=16, font_family="PPM")
        self.det_moyenne = ft.Text(size=16, font_family="PPM")
        self.det_rang = ft.Text(size=16, font_family="PPM")
        self.det_rating = ft.Text(size=16, font_family="PPM")
        self.bt_print_report = MyMiniIcon(
            ft.Icons.PRINT, languages[lang]['print'], 'black', None, self.download_report_book_second_cycle
        )
        self.bt_print_report.visible = False
        self.load_bar = ft.ProgressBar(
            width=150, height=5, border_radius=16, color=BASE_COLOR, bgcolor='#f0f0f6'
        )
        self.load_text = ft.Text(
            languages[lang]['data loading'], size=12, font_family='PPM', color="grey"
        )

        self.details_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=800, height=750,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(bottom=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(top_left=8, top_right=8),
                            content=ft.Row(
                                controls=[
                                    ft.Text(languages[lang]['note details'], size=16, font_family='PPB'),
                                    ft.IconButton(
                                        'close', icon_color='black87', bgcolor=CT_BGCOLOR, scale=0.7,
                                        on_click=self.close_details_window
                                    ),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                            )
                        ),
                        ft.Container(
                            bgcolor="white", padding=20, border=ft.border.only(top=ft.BorderSide(1, CT_BORDER_COLOR)),
                            border_radius=ft.border_radius.only(bottom_left=8, bottom_right=8), expand=True,
                            content=ft.Column(
                                expand=True, controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Row(
                                                controls=[
                                                    self.det_zone,
                                                    ft.Column([self.det_name, self.det_surname], spacing=0)
                                                ]
                                            ),
                                            ft.Row(
                                                controls=[
                                                    self.bt_print_report, self.load_bar, self.load_text
                                                ]
                                            )
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, border_radius=16, bgcolor='grey50',
                                        content=ft.Row(
                                            controls=[
                                                # class...
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon('roofing', color='black', size=16),
                                                                ft.Text(languages[lang]['class'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_class

                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon('calendar_month_outlined', color='black', size=16),
                                                        self.det_sequence
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.BAR_CHART_OUTLINED, color='black', size=16),
                                                                ft.Text(languages[lang]['average'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_moyenne

                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.PIE_CHART_SHARP, color='black', size=16),
                                                                ft.Text(languages[lang]['rank'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_rang
                                                    ]
                                                ),
                                                ft.Row(
                                                    controls=[
                                                        ft.Row(
                                                            controls=[
                                                                ft.Icon(ft.Icons.REQUEST_QUOTE, color='black', size=16),
                                                                ft.Text(languages[lang]['rating'], size=12,
                                                                        font_family='PPM', color='black')
                                                            ]
                                                        ), self.det_rating

                                                    ]
                                                ),
                                            ],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ),
                                    ft.Divider(color=ft.Colors.TRANSPARENT),
                                    ft.ListView(
                                        expand=True, controls=[self.det_table]
                                    )
                                ]

                            )
                        )
                    ], spacing=0
                )
            )
        )

        self.content = ft.Stack(
            alignment=ft.alignment.center,
            controls=[
                self.main_window, self.details_window
            ]
        )
        self.on_mount()

    def hide_one_window(self, window_to_hide: object):
        """
        This function helps to make menus clickable
        :param window_to_hide:
        :return:
        """
        window_to_hide.scale = 0

        self.cp.left_menu.disabled = False
        self.cp.top_menu.disabled = False
        self.main_window.disabled = False
        self.cp.left_menu.opacity = 1
        self.cp.top_menu.opacity = 1
        self.main_window.opacity = 1
        self.cp.page.update()

    def show_one_window(self, window_to_show):
        """
        This function helps to make menus non-clickable
        :param window_to_show:
        :return:
        """
        window_to_show.scale = 1

        self.cp.left_menu.disabled = True
        self.cp.top_menu.disabled = True
        self.main_window.disabled = True
        self.cp.left_menu.opacity = 0.3
        self.cp.top_menu.opacity = 0.3
        self.main_window.opacity = 0.3
        self.cp.page.update()

    @staticmethod
    def run_async_in_thread(coro):
        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(coro)
            loop.close()

        thread = threading.Thread(target=runner)
        thread.start()

    async def on_init_async(self):
        await self.load_datas()

    def on_mount(self):
        self.run_async_in_thread(self.on_init_async())

    async def load_datas(self):
        year_id = self.cp.year_id
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_sequence_averages_with_details(access_token, year_id)

        nb_success = 0
        nb_fails = 0

        self.table.rows.clear()

        for i, item in enumerate(datas):
            if i == 0:
                for clef in item.keys():
                    print(f"{clef}: {item[clef]}")

            if item['value'] >= 10:
                status_icon = ColoredIcon(ft.Icons.CHECK_CIRCLE, 'teal', 'teal50')
                nb_success += 1
            else:
                status_icon = ColoredIcon(ft.Icons.CLOSE, 'red', 'red50')
                nb_fails += 1

            count_sup = 0
            for element in datas:
                if element['class_code'] == item['class_code']:
                    if element['value'] > item['value']:
                        count_sup += 1

            rang = count_sup + 1

            new_data: dict = {'rang': rang}
            for clef in item.keys():
                new_data[clef] = item[clef]

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                        ft.DataCell(ft.Text(f"{item['class_code']}")),
                        ft.DataCell(ft.Text(f"{item['sequence']}")),
                        ft.DataCell(ft.Text(f"{item['points']}")),
                        ft.DataCell(ft.Text(f"{item['total_coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['value']:.2f}")),
                        ft.DataCell(status_icon),
                        ft.DataCell(ft.Text(f"{rang}")),
                        ft.DataCell(
                            MyMiniIcon(
                                ft.Icons.FORMAT_LIST_BULLETED_OUTLINED,
                                languages[self.lang]['details'], 'grey', new_data, self.open_details_window
                            )
                        )
                    ]
                )
            )

        self.nb_success.value = add_separator(nb_success)
        self.nb_fails.value = add_separator(nb_fails)

        if nb_success / len(datas) < 1:
            self.success_rate.value = f"{(nb_success * 100 / len(datas)):.2f} %"
        else:
            self.success_rate.value = f"{(nb_success * 100 / len(datas)):.0f} %"

        self.cp.page.update()

    async def filter_datas(self, e):
        year_id = self.cp.year_id
        access_token = self.cp.page.client_storage.get('access_token')
        datas = await get_sequence_averages_with_details(access_token, year_id)

        nb_success = 0
        nb_fails = 0

        search = self.search.value.lower() if self.search.value else ''
        filtered_datas = list(filter(
            lambda x: search in x['student_name'].lower() or
                      search in x['student_surname'].lower() or
                      search in x['class_code'].lower(), datas
        ))
        self.table.rows.clear()

        for item in filtered_datas:

            if item['value'] >= 10:
                status_icon = ColoredIcon(ft.Icons.CHECK_CIRCLE, 'teal', 'teal50')
                nb_success += 1
            else:
                status_icon = ColoredIcon(ft.Icons.CLOSE, 'red', 'red50')
                nb_fails += 1

            count_sup = 0
            for element in datas:
                if element['class_code'] == item['class_code']:
                    if element['value'] > item['value']:
                        count_sup += 1

            rang = count_sup + 1

            new_data: dict = {'rang': rang}
            for clef in item.keys():
                new_data[clef] = item[clef]

            self.table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['student_name']} {item['student_surname']}".upper())),
                        ft.DataCell(ft.Text(f"{item['class_code']}")),
                        ft.DataCell(ft.Text(f"{item['sequence']}")),
                        ft.DataCell(ft.Text(f"{item['points']}")),
                        ft.DataCell(ft.Text(f"{item['total_coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['value']:.2f}")),
                        ft.DataCell(status_icon),
                        ft.DataCell(ft.Text(f"{rang}")),
                        ft.DataCell(
                            MyMiniIcon(
                                ft.Icons.FORMAT_LIST_BULLETED_OUTLINED,
                                languages[self.lang]['details'], 'grey', new_data, self.open_details_window
                            )
                        )
                    ]
                )
            )

        self.cp.page.update()

    def on_search_change(self, e):
        self.run_async_in_thread(self.filter_datas(e))

    async def load_details_by_student(self, e):
        access_token = self.cp.page.client_storage.get('access_token')
        year_id = self.cp.year_id

        self.det_image.foreground_image_src = e.control.data['student_image']
        self.det_name.value = e.control.data['student_name']
        self.det_surname.value = e.control.data['student_surname']
        self.det_sequence.value = languages[self.lang][e.control.data['sequence']]
        self.det_rang.value = e.control.data['rang']
        self.det_class.value = e.control.data['class_code']
        self.det_rating.value = get_rating(e.control.data['value'])
        self.det_moyenne.value = f"{e.control.data['value']:.2f}"
        self.cp.page.update()

        self.show_one_window(self.details_window)

        details_notes = await get_notes_by_student_sequence_year(
            access_token, e.control.data['student_id'], e.control.data['sequence'], year_id
        )

        # on met sur le bouton les différentes data à imprimer
        print_dico_data: dict = dict()
        class_statistics: dict = await get_class_statistics_sequence(access_token, year_id, e.control.data['class_id'], e.control.data['sequence'])

        print("parameters statistics_______________________________________________")
        for param in (access_token, year_id, e.control.data['class_id'], e.control.data['sequence']):
            print(param)

        student_infos = await get_student_basic_infos(access_token, e.control.data['student_id'])
        student_discipline = await get_student_discipline_by_sequence(
            access_token, year_id, e.control.data['student_id'], e.control.data['sequence']
        )
        print_dico_data['student statistics'] = e.control.data  # un dictionnaire
        print_dico_data['details notes'] = details_notes  # liste de dictionnaires
        print_dico_data['class statistics'] = class_statistics  # un dictionnaire
        print_dico_data['student info'] = student_infos  # un dictionnaire
        print_dico_data['student discipline'] = student_discipline  # liste de dictionnaires
        self.bt_print_report.data = print_dico_data

        # on vérifie que les infos sont correctes....
        for clef in print_dico_data.keys():
            print(
                f"clé: {clef}\n"
                f"{print_dico_data[clef]}"
            )

        # on remplit la table des notes...
        self.det_table.rows.clear()
        for item in details_notes:

            if item['value'] >= 15:
                status_color= ft.Colors.LIGHT_GREEN
                status_icon = ft.Icons.RECOMMEND_ROUNDED
            elif item['value'] <= 7:
                status_color = 'red'
                status_icon = ft.Icons.MOOD_BAD_ROUNDED
            else:
                status_color = None
                status_icon = None

            self.det_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(f"{item['subject_short_name']}")),
                        ft.DataCell(
                            ft.Row(
                                controls=[
                                    ft.Text(f"{item['value']}"),
                                    ft.Icon(status_icon, color=status_color, size=16)
                                ], spacing=3
                            )
                        ),
                        ft.DataCell(ft.Text(f"{item['coefficient']}")),
                        ft.DataCell(ft.Text(f"{item['value'] * item['coefficient']:.2f}")),
                        ft.DataCell(ft.Text(f"{get_rating(item['value'])}")),
                    ]
                )
            )

        self.bt_print_report.visible = True
        self.load_text.visible = False
        self.load_bar.visible = False
        self.cp.page.update()

    def open_details_window(self, e):
        self.run_async_in_thread(self.load_details_by_student(e))

    def close_details_window(self, e):
        self.det_table.rows.clear()
        self.bt_print_report.visible = False
        self.load_bar.visible = True
        self.load_text.visible = True
        self.hide_one_window(self.details_window)

    def download_report_book_second_cycle(self, e):
        buffer = io.BytesIO()
        can = Canvas(buffer, pagesize=A4)

        gauche, droite, y = 4.25, 17.25, 28

        self.create_pdf_fonts()
        student_infos: dict = e.control.data['student info']
        students_statistics = e.control.data['student statistics']
        class_statistics: dict = e.control.data['class statistics']
        student_discipline: list = e.control.data['student discipline']
        details_notes: list = e.control.data['details notes']
        year_short = self.cp.year_short
        sequence = self.cp.active_sequence.data

        def draw_headers():
            # on commence par les entêtes du bulletin...
            def draw_headers_left():
                # A gauche
                can.setFillColorRGB(0, 0, 0)
                can.setFont("calibri bold", 10)
                can.drawCentredString(gauche * cm, 28.5 * cm, school_republic_fr.upper())
                can.setFont("calibri z", 9)
                can.drawCentredString(gauche * cm, 28.1 * cm, national_devise_fr.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 27.7 * cm, "*************")
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 27.3 * cm, school_delegation_fr.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(gauche * cm, 26.9 * cm, school_name_fr.upper())

            def draw_headers_right():
                # droite
                can.setFillColorRGB(0, 0, 0)
                can.setFont("calibri bold", 10)
                can.drawCentredString(droite * cm, 28.5 * cm, school_republic_en.upper())
                can.setFont("calibri z", 9)
                can.drawCentredString(droite * cm, 28.1 * cm, national_devise_en.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 27.7 * cm, "*************")
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 27.3 * cm, school_delegation_en.upper())
                can.setFont("calibri", 9)
                can.drawCentredString(droite * cm, 26.9 * cm, school_name_en.upper())

            def draw_school_logo():
                logo_response = requests.get(logo_url)
                image = ImageReader(io.BytesIO(logo_response.content))
                image_width, image_height = 3.5 * cm, 3.5 * cm
                can.drawImage(image, 9 * cm, 26 * cm, width=image_width, height=image_height)

            def draw_year_and_sequence():
                can.setFont("calibri bold", 15)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(
                    10.5 * cm, 25.6 * cm,
                    f"{languages[self.lang]['report card']} - {sequence}".upper()
                )

                can.setFont("calibri", 12)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(
                    10.5 * cm, 25.1 * cm,
                    f"{languages[self.lang]['academic year']} {year_short - 1} / {year_short}"
                )

            # on execute les fonctions...
            draw_headers_left()
            draw_headers_right()
            draw_school_logo()
            draw_year_and_sequence()

            # infos sur l'élève ...
            def draw_student_lines():
                # Lignes horizontales
                # 1ere ligne
                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                can.line(4 * cm, 24.6 * cm, 20 * cm, 24.6 * cm)

                # Lignes du milieu
                can.line(4 * cm, 23.9 * cm, 20 * cm, 23.9 * cm)
                can.line(4 * cm, 23.2 * cm, 20 * cm, 23.2 * cm)
                can.line(4 * cm, 22.5 * cm, 16 * cm, 22.5 * cm)

                # Dernière ligne
                can.line(4 * cm, 21.3 * cm, 20 * cm, 21.3 * cm)

                # Lignes verticales
                can.setStrokeColorRGB(0.3, 0.3, 0.3)
                # 1ere ligne
                can.line(4 * cm, 24.6 * cm, 4 * cm, 21.3 * cm)

                can.line(11 * cm, 23.2 * cm, 11 * cm, 22.5 * cm)
                can.line(13.5 * cm, 23.9 * cm, 13.5 * cm, 23.2 * cm)
                can.line(16 * cm, 24.6 * cm, 16 * cm, 21.3 * cm)

                # Dernière ligne
                can.line(20 * cm, 24.6 * cm, 20 * cm, 21.3 * cm)

            def draw_student_informations():

                # champs d'informations
                can.setFont("calibri", 10)
                can.drawString(4.2 * cm, 24.1 * cm, "Nom de l'élève:")
                can.drawString(16.2 * cm, 24.1 * cm, "Classe:")
                can.drawString(4.2 * cm, 23.4 * cm, "Date et lieu de naissance:")
                can.drawString(13.8 * cm, 23.4 * cm, "Genre:")
                can.drawString(16.2 * cm, 23.4 * cm, "Effectif:")
                can.setFillColorRGB(1, 0, 0)
                can.drawString(4.2 * cm, 22.7 * cm, "Identifiant unique:")
                can.setFillColorRGB(0, 0, 0)
                can.drawString(11.2 * cm, 22.7 * cm, "Redoublant: oui          non")
                can.drawString(16.2 * cm, 22.7 * cm, "Professeur principal:")
                can.setFillColorRGB(0, 0, 0)
                can.drawString(4.2 * cm, 22 * cm, "Noms et contact des parents/tuteurs:")

                # remplissage des informations
                can.setFont("calibri bold", 11)
                can.setFillColorRGB(0, 0, 0)
                can.drawString(6.7 * cm, 24.1 * cm, f"{student_infos['name']} {student_infos['surname']}")  # Nom et prénom élève...
                can.drawString(17.4 * cm, 24.1 * cm, f"")  # classe...
                can.drawString(8 * cm, 23.4 * cm, f"{student_infos['birth_date']} {student_infos['birth_place']}")  # Date et lieu de naissance
                can.drawString(15.2 * cm, 23.4 * cm, f"{student_infos['gender']}")  # sexe
                can.drawString(17.8 * cm, 23.4 * cm, f"")  # Effectif
                can.drawString(4.2 * cm, 21.5 * cm, f"{student_infos['contact']}")  # Contact parents
                #on trouve le prof titulaire...
                can.drawString(16.2 * cm, 22.3 * cm, f"")  # Nom professeur...
                can.drawString(16.2 * cm, 21.9 * cm, f"")  # prénom Professeur...

            draw_student_lines()
            draw_student_informations()

        def draw_footer():
            # Pied de page
            foot = (f"Bulletin / {year_short - 1}-{year_short} / {sequence}"
                    f"{student_infos['name']} {student_infos['surname']}"
            ).upper()
            can.setFont("calibri", 9)
            can.setFillColorRGB(0.5, 0.5, 0.5)
            can.drawCentredString(10.5 * cm, 0.5 * cm, foot)

        def draw_notes_details():
            # divisions pour les lignes horizontales
            b1, b2, b3, b4, b5, b6, b7, b8, = 1, 10, 11.5, 12.5, 14, 15, 17, 20

            # divisions pour les lignes verticales
            m1 = (b1 + b2) / 2
            m2 = (b2 + b3) / 2
            m3 = (b3 + b4) / 2
            m4 = (b4 + b5) / 2
            m5 = (b5 + b6) / 2
            m6 = (b6 + b7) / 2
            m7 = (b7 + b8) / 2

            def draw_titles():
                can.setStrokeColorRGB(0.3, 0.3, 0.3)

                # Lignes horizontales
                can.line(1 * cm, 21 * cm, 20 * cm, 21 * cm)
                can.line(1 * cm, 20.4 * cm, 20 * cm, 20.4 * cm)

                # Lignes verticales
                can.line(b1 * cm, 20.4 * cm, b1 * cm, 21 * cm)
                can.line(b2 * cm, 20.4 * cm, b2 * cm, 21 * cm)
                can.line(b3 * cm, 20.4 * cm, b3 * cm, 21 * cm)
                can.line(b4 * cm, 20.4 * cm, b4 * cm, 21 * cm)
                can.line(b5 * cm, 20.4 * cm, b5 * cm, 21 * cm)
                can.line(b6 * cm, 20.4 * cm, b6 * cm, 21 * cm)
                can.line(b7 * cm, 20.4 * cm, b7 * cm, 21 * cm)
                can.line(b8 * cm, 20.4 * cm, b8 * cm, 21 * cm)

                can.setFont("calibri bold", 10)
                can.setFillColorRGB(0, 0, 0)
                can.drawCentredString(m1 * cm, 20.6 * cm, "Matiere")
                can.drawCentredString(m2 * cm, 20.6 * cm, "M/20")
                can.drawCentredString(m3 * cm, 20.6 * cm, "Coef")
                can.drawCentredString(m4 * cm, 20.6 * cm, "M x coef")
                can.drawCentredString(m5 * cm, 20.6 * cm, "Cote")

                can.setFillColorRGB(1, 0, 0)
                can.drawCentredString(m6 * cm, 20.6 * cm, "Min-Max")
                can.drawCentredString(m7 * cm, 20.6 * cm, "Appreciation")
                can.setFillColorRGB(0, 0, 0)

            draw_titles()

            y = 20.6

            group1, group2, group3 = [], [], []
            general_points = 0
            general_coefficients = 0

            # Remplissage des matières dans les groupes
            for row in details_notes:
                if row['subject_group'] == "g1":
                    group1.append(
                        {
                            "subject_name": row['subject_name'], "coefficient": row['coefficient'], "note": row['value'],
                            "total": row['value']*row['coefficient'], "cote": get_rating(row['value'])
                        }
                    )
                elif row['subject_group'] == 'g2':
                    group2.append(
                        {
                            "subject_name": row['subject_name'], "coefficient": row['coefficient'], "note": row['value'],
                            "total": row['value'] * row['coefficient'], "cote": get_rating(row['value'])
                        }
                    )
                else:
                    group3.append(
                        {
                            "subject_name": row['subject_name'], "coefficient": row['coefficient'], "note": row['value'],
                            "total": row['value'] * row['coefficient'], "cote": get_rating(row['value'])
                        }
                    )

            groups = [
                {"group name": "1er groupe", "group datas": group1},
                {"group name": "2e groupe", "group datas": group2},
                {"group name": "3e groupe", "group datas": group3},
            ]

        # on exécute les fonctions...
        draw_headers()
        draw_footer()

        # on enregistre le document
        can.save()
        buffer.seek(0)

        # Upload Supabase
        file_path = f"Bulletin_{student_infos['name']}_{student_infos['surname']}_{sequence}_{uuid.uuid4().hex[:6]}.pdf"
        supabase_client.storage.from_(DOCUMENTS_BUCKET).upload(
            path=file_path,
            file=buffer.getvalue(),
            file_options={"content-type": "application/pdf"}
        )
        signed_url_response = supabase_client.storage.from_(DOCUMENTS_BUCKET).create_signed_url(
            file_path, 3600 * 24 * 365
        )
        signed_url = signed_url_response.get("signedURL")
        self.cp.page.launch_url(signed_url)

    @staticmethod
    def create_pdf_fonts():
        pdfmetrics.registerFont(TTFont('vinci sans medium', "assets/fonts/vinci_sans_medium.ttf"))
        pdfmetrics.registerFont(TTFont('vinci sans regular', "assets/fonts/vinci_sans_regular.ttf"))
        pdfmetrics.registerFont(TTFont('vinci sans bold', "assets/fonts/vinci_sans_bold.ttf"))
        pdfmetrics.registerFont(TTFont('calibri', "assets/fonts/calibri.ttf"))
        pdfmetrics.registerFont(TTFont('calibri italic', "assets/fonts/calibrii.ttf"))
        pdfmetrics.registerFont(TTFont('calibri bold', "assets/fonts/calibrib.ttf"))
        pdfmetrics.registerFont(TTFont('calibri z', "assets/fonts/calibriz.ttf"))
        pdfmetrics.registerFont(TTFont('Poppins SemiBold', "assets/fonts/Poppins-SemiBold.ttf"))
        pdfmetrics.registerFont(TTFont('Poppins Bold', "assets/fonts/Poppins-Bold.ttf"))


from components import MyButton, MyIconButton, MyMiniIcon, ColoredIcon, ColoredButton, BoxStudentNote
from utils.styles import *
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading, openpyxl, uuid
import pandas as pd
from io import BytesIO
from services.async_functions.report_book_functions import *
from utils.useful_functions import add_separator, get_rating

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
        self.det_sequence = ft.Text(size=13, font_family="PPB")
        self.det_class = ft.Text(size=13, font_family="PPB")
        self.det_moyenne = ft.Text(size=13, font_family="PPB")
        self.det_rang = ft.Text(size=13, font_family="PPB")
        self.det_rating = ft.Text(size=13, font_family="PPB")
        self.bt_print_report = MyMiniIcon(
            ft.Icons.PRINT, languages[lang]['print'], 'black', None, None
        )

        self.details_window = ft.Card(
            elevation=50, shape=ft.RoundedRectangleBorder(radius=16),
            scale=ft.Scale(0), animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_IN),
            content=ft.Container(
                bgcolor=CT_BGCOLOR, padding=0, border_radius=16, width=750, height=750,
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
                                            self.bt_print_report
                                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        padding=10, border_radius=16, bgcolor=BASE_COLOR,
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

        for item in datas:

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

        self.details_window.scale = 1

        # désactiver les menus
        self.main_window.opacity = 0.3
        self.main_window.disabled = True
        self.cp.left_menu.opacity = 0.3
        self.cp.left_menu.disabled = True
        self.cp.top_menu.opacity = 0.3
        self.cp.top_menu.disabled = True
        self.cp.page.update()

        self.det_image.foreground_image_src = e.control.data['student_image']
        self.det_name.value = e.control.data['student_name']
        self.det_surname.value = e.control.data['student_surname']
        self.det_sequence.value = languages[self.lang][e.control.data['sequence']]
        self.det_rang.value = e.control.data['rang']
        self.det_class.value = e.control.data['class_code']
        self.det_rating.value = get_rating(e.control.data['value'])
        self.det_moyenne.value = f"{e.control.data['value']:.2f}"
        self.cp.page.update()

        print('student_id', e.control.data['student_id'])
        print('sequence', e.control.data['sequence'])
        print('year_id', e.control.data['year_id'])

        details_notes = await get_notes_by_student_sequence_year(
            access_token, e.control.data['student_id'], e.control.data['sequence'], year_id
        )

        print_dico_data: dict = dict()
        print_dico_data['student_condensed'] = e.control.data
        print_dico_data['details_notes'] = details_notes

        # on remplit la table des notes...
        self.det_table.rows.clear()
        for item in details_notes:

            if item['value'] >= 15:
                status_color= 'green'
                status_icon = ft.Icons.CIRCLE_SHARP
            elif item['value'] <= 7:
                status_color = 'red'
                status_icon = ft.Icons.CIRCLE
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

        self.cp.page.update()

    def open_details_window(self, e):
        self.run_async_in_thread(self.load_details_by_student(e))

    def close_details_window(self, e):
        self.details_window.scale = 0

        # désactiver les menus
        self.main_window.opacity = 1
        self.main_window.disabled = False
        self.cp.left_menu.opacity = 1
        self.cp.left_menu.disabled = False
        self.cp.top_menu.opacity = 1
        self.cp.top_menu.disabled = False
        self.cp.page.update()

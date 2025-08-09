import flet as ft
from components import MyButton, MyIconButton, MyMiniIcon, ColoredIcon, ColoredButton, ColoredIconButton
from utils.styles import search_style, drop_style, login_style, other_style, datatable_style, cool_style
from utils.couleurs import *
from translations.translations import languages
import os, mimetypes, asyncio, threading
from services.async_functions.fees_functions import *
from utils.useful_functions import format_number, add_separator


class SchoolFees(ft.Container):
    def __init__(self, cp: object):
        super().__init__(
            expand=True
        )
        # parent container (Home) ___________________________________________________________
        self.cp = cp
        lang = self.cp.language
        self.lang = lang

        # main window ______________________________________________________________

        # Kpi
        self.expected_amount = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.amount_collected = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.amount_stayed = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.recovery_rate = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)
        self.nb_transactions = ft.Text('-', size=28, font_family="PPM", weight=ft.FontWeight.BOLD)

        self.ct_expected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.BAR_CHART_ROUNDED, 'indigo', 'indigo50'),
                            ft.Text(languages[lang]['expected'].upper(), size=12, font_family='PPI', color='indigo')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.expected_amount,
                            ft.Text(languages[lang]['expected amount'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_collected = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.RECEIPT_SHARP, 'teal', 'teal50'),
                            ft.Text(languages[lang]['received'].upper(), size=12, font_family='PPI', color='teal')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_collected,
                            ft.Text(languages[lang]['collected amount'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_remaining = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.REAL_ESTATE_AGENT, 'deeporange', 'deeporange50'),
                            ft.Text(languages[lang]['remaining'].upper(), size=12, font_family='PPI', color='deeporange')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.amount_stayed,
                            ft.Text(languages[lang]['remaining balance'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_rate = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.PIE_CHART_SHARP, 'green', 'green50'),
                            ft.Text(languages[lang]['rate'].upper(), size=12, font_family='PPI', color='green')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.recovery_rate,
                            ft.Text(languages[lang]['recovery rate'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.ct_transactions = ft.Container(
            width=170, height=120, padding=10, border_radius=24,
            bgcolor='white', content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ColoredIcon(ft.Icons.MONETIZATION_ON, 'amber', 'amber50'),
                            ft.Text(languages[lang]['number'].upper(), size=12, font_family='PPI', color='amber')
                        ], alignment=ft.MainAxisAlignment.START
                    ),
                    ft.Column(
                        controls=[
                            self.nb_transactions,
                            ft.Text(languages[lang]['nb transactions'], size=11, font_family='PPI', color='grey')
                        ], spacing=0
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )


        # widget
        self.search_class = ft.Dropdown(
            **drop_style,
            prefix_icon=ft.Icons.ROOFING, label=languages[lang]['class'], width=180,
            on_change=None, menu_height=200,
            options=[ft.dropdown.Option(key=" ", text=f"global")], value=" "
        )
        self.search_tranche = ft.Dropdown(
            **drop_style, width=160, label=languages[lang]['fees part'], value='tout',
            options=[
                ft.dropdown.Option(
                    key=choice['clé'], text=f"{choice['valeur']}"
                )
                for choice in [
                    {'clé': 'tranche 1', 'valeur': languages[lang]['fees part 1']},
                    {'clé': 'tranche 2', 'valeur': languages[lang]['fees part 2']},
                    {'clé': 'tranche 3', 'valeur': languages[lang]['fees part 3']},
                    {'clé': 'tout', 'valeur': 'global'},
                ]
            ]
        )
        self.table = ft.DataTable(
            **datatable_style, expand=True,
            columns=[
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon('person_outlined', size=20, color='black45'),
                            ft.Text(languages[lang]['name']),
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon('roofing', size=20, color='black45'),
                            ft.Text(languages[lang]['class']),
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ATTACH_MONEY, size=20, color='black45'),
                            ft.Text(languages[lang]['amount paid']),
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.CHECK_BOX_OUTLINED, size=20, color='black45'),
                            ft.Text(languages[lang]['status']),
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                        ft.Icon(ft.Icons.REAL_ESTATE_AGENT_OUTLINED, size=20, color='black45'),
                            ft.Text(languages[lang]['remaining balance']),
                        ]
                    )
                ),
                ft.DataColumn(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, size=20, color='black45'),
                            ft.Text('Actions'),
                        ]
                    )
                ),
            ]
        )
        self.main_window = ft.Container(
            expand=True, content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.ct_expected, ft.VerticalDivider(),
                            self.ct_collected, ft.VerticalDivider(),
                            self.ct_rate, ft.VerticalDivider(),
                            self.ct_remaining, ft.VerticalDivider(),
                            self.ct_transactions
                        ]
                    ),
                    ft.Row(
                        expand=True,
                        controls=[
                            ft.Container(
                                padding=0, border_radius=16, border=ft.border.all(1, 'white'),
                                expand=True, bgcolor='white', content=ft.Column(
                                    controls=[
                                        ft.Container(
                                            padding=20, content=ft.Row(
                                                controls=[
                                                    ColoredButton(
                                                        languages[lang]['make a payment'], ft.Icons.ADD_CARD_OUTLINED, None
                                                    ),
                                                    ft.Row(
                                                        controls=[
                                                            self.search_class, self.search_tranche,
                                                            ColoredIconButton(
                                                                ft.Icons.FILTER_ALT_OUTLINED, languages[lang]['filter'],
                                                                'black', BASE_COLOR, self.click_on_filter
                                                            ),
                                                            ColoredIconButton(
                                                                ft.Icons.FILTER_ALT_OFF_OUTLINED, languages[lang]['filter'],
                                                                'black', BASE_COLOR, None
                                                            ),
                                                        ]
                                                    )
                                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                            )
                                        ),
                                        ft.Divider(color=ft.Colors.TRANSPARENT),
                                        ft.ListView(expand=True, controls=[self.table]),
                                        ft.Container(
                                            padding=20,
                                            content=ft.Row(
                                                controls=[
                                                    ft.Text(languages[lang]['data extraction'].upper(), size=12,
                                                            font_family='PPB'),
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
                                        )
                                    ]
                                )
                            ),
                            ft.Column(
                                controls=[

                                ]
                            )
                        ]
                    )
                ]
            )
        )

        self.content = ft.Stack(
            expand=True,
            controls=[
                self.main_window
            ], alignment=ft.alignment.center
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
        access_token = self.cp.page.client_storage.get("access_token")
        all_classes = await get_all_classes_basic_info(access_token)

        for one_classe in all_classes:
            self.search_class.options.append(
                ft.dropdown.Option(
                    key=one_classe['id'], text=f"{one_classe['code']}"
                )
            )

        self.cp.page.update()

    async def filter_datas(self, e):
        access_token = self.cp.page.client_storage.get("access_token")

        # cas du raport global...
        if self.search_tranche.value == 'tout':

            # si le champs classe est vide...
            if self.search_class.value == " ":
                datas = await get_global_students_fees_status(access_token)
                search_class = self.search_class.value if self.search_class.value else ''

                self.table.rows.clear()

                total_fees = await get_total_school_fees_for_active_year(access_token)
                self.expected_amount.value = format_number(len(datas) * total_fees)

                paid = 0

                for data in datas:
                    paid += data['total_paid']
                    if data['status']:
                        color = 'teal'
                        bgcolor = 'teal50'
                        icone = ft.Icons.CHECK
                        text = languages[self.lang]['sold out']
                    else:
                        color = 'red'
                        bgcolor = 'red50'
                        icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                        text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                                ft.DataCell(ft.Text(f"{data['class code']}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=bgcolor, border_radius=12, padding=5,
                                        # border=ft.border.all(1, color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(icone, size=14, color=color),
                                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                                ft.DataCell(ft.Text(f"{add_separator(data['total stayed'])}")),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None)
                                        ]
                                    )
                                ),

                            ]
                        )
                    )

                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(len(datas) * total_fees - paid)
                self.recovery_rate.value = f"{(paid * 100 / (len(datas) * total_fees)):.2f}%"
                self.nb_transactions.value = add_separator(len(datas))

                self.cp.page.update()

            # si le champs classe est rempli...
            else:
                datas = await get_global_students_fees_status_by_class(access_token, self.search_class.value)
                search_class = self.search_class.value if self.search_class.value else ''

                self.table.rows.clear()

                total_fees = await get_total_school_fees_for_active_year(access_token)
                self.expected_amount.value = format_number(len(datas) * total_fees)

                paid = 0

                for data in datas:
                    paid += data['total_paid']
                    if data['status']:
                        color = 'teal'
                        bgcolor = 'teal50'
                        icone = ft.Icons.CHECK
                        text = languages[self.lang]['sold out']
                    else:
                        color = 'red'
                        bgcolor = 'red50'
                        icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                        text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                                ft.DataCell(ft.Text(f"{data['class code']}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=bgcolor, border_radius=12, padding=5,
                                        # border=ft.border.all(1, color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(icone, size=14, color=color),
                                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                                ft.DataCell(ft.Text(f"{add_separator(data['total stayed'])}")),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None)
                                        ]
                                    )
                                ),

                            ]
                        )
                    )

                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(len(datas) * total_fees - paid)
                self.recovery_rate.value = f"{(paid * 100 / (len(datas) * total_fees)):.2f}%"
                self.nb_transactions.value = add_separator(len(datas))

                self.cp.page.update()

        #  cas du rapport par tranche...
        else:
            # si le champs classe est vide...
            if self.search_class.value is None:
                datas = await get_students_fees_status_by_part(access_token, self.search_tranche.value)
                self.table.rows.clear()

                total_fees = await get_total_school_fees_for_active_year(access_token)
                self.expected_amount.value = format_number(len(datas) * total_fees)

                paid = 0

                for data in datas:
                    paid += data['total_paid']
                    if data['status']:
                        color = 'teal'
                        bgcolor = 'teal50'
                        icone = ft.Icons.CHECK
                        text = languages[self.lang]['sold out']
                    else:
                        color = 'red'
                        bgcolor = 'red50'
                        icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                        text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                                ft.DataCell(ft.Text(f"{data['class code']}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=bgcolor, border_radius=12, padding=5,
                                        # border=ft.border.all(1, color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(icone, size=14, color=color),
                                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                                ft.DataCell(ft.Text(f"{add_separator(data['total stayed'])}")),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None)
                                        ]
                                    )
                                ),

                            ]
                        )
                    )

                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(len(datas) * total_fees - paid)
                self.recovery_rate.value = f"{(paid * 100 / (len(datas) * total_fees)):.2f}%"
                self.nb_transactions.value = add_separator(len(datas))

                self.cp.page.update()

            #si le champs classe est rempli...
            else:
                sc = self.search_class.value
                datas = await get_students_fees_status_for_part_and_class(access_token, self.search_tranche.value, sc)
                self.table.rows.clear()

                total_fees = await get_total_school_fees_for_active_year(access_token)
                self.expected_amount.value = format_number(len(datas) * total_fees)

                paid = 0

                for data in datas:
                    paid += data['total_paid']
                    if data['status']:
                        color = 'teal'
                        bgcolor = 'teal50'
                        icone = ft.Icons.CHECK
                        text = languages[self.lang]['sold out']
                    else:
                        color = 'red'
                        bgcolor = 'red50'
                        icone = ft.Icons.INDETERMINATE_CHECK_BOX_OUTLINED
                        text = languages[self.lang]['on going']

                    self.table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(f"{data['name']} {data['surname']}".upper())),
                                ft.DataCell(ft.Text(f"{data['class code']}")),
                                ft.DataCell(ft.Text(f"{add_separator(data['total_paid'])}")),
                                ft.DataCell(
                                    ft.Container(
                                        bgcolor=bgcolor, border_radius=12, padding=5,
                                        # border=ft.border.all(1, color),
                                        content=ft.Row(
                                            controls=[
                                                ft.Row(
                                                    controls=[
                                                        ft.Icon(icone, size=14, color=color),
                                                        ft.Text(text, size=11, font_family='PPM', color=color)
                                                    ], spacing=3
                                                )
                                            ],
                                            alignment=ft.MainAxisAlignment.CENTER
                                        )
                                    )
                                ),
                                ft.DataCell(ft.Text(f"{add_separator(data['total stayed'])}")),
                                ft.DataCell(
                                    ft.Row(
                                        controls=[
                                            MyMiniIcon(ft.Icons.FORMAT_LIST_BULLETED_SHARP, '', 'grey', data, None)
                                        ]
                                    )
                                ),

                            ]
                        )
                    )

                self.amount_collected.value = format_number(paid)
                self.amount_stayed.value = format_number(len(datas) * total_fees - paid)
                self.recovery_rate.value = f"{(paid * 100 / (len(datas) * total_fees)):.2f}%"
                self.nb_transactions.value = add_separator(len(datas))

                self.cp.page.update()

    def click_on_filter(self, e):
        self.run_async_in_thread(self.filter_datas(e))


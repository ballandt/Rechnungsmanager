from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128, qr


class Bill:
    """Bill PDF Creator Class"""
    def __init__(self, bill_id, bill_year, database, direction):
        self.provider = database.bill_provider_info(bill_id, bill_year)
        self.bill = database.bill_info(bill_id, bill_year)
        self.customer = database.bill_customer_info(bill_id, bill_year)
        self.services = database.bill_services_info(bill_id, bill_year)

        self.canvas = canvas.Canvas(direction)

        pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
        pdfmetrics.registerFont(TTFont('ArialBd', 'ArialBd.ttf'))
        pdfmetrics.registerFont(TTFont('Vera', 'Calibri.ttf'))

    def save(self):
        """Saves PDF file. Has to be called separately after initialising the instance."""
        # Barcode encoding the bill id
        bar_code = code128.Code128("-".join([str(self.bill[5]), f"{self.bill[0]:03d}"]), barWidth=1.3, barHeight=15)
        bar_code.drawOn(self.canvas, 35, 790)

        y = 750 # cursor for further body elements

        # Provider address
        self.canvas.setFont("Arial", 8)
        self.canvas.drawString(50, y, " \u00b7 ".join([" ".join(self.provider[2:4]), " ".join(self.provider[5:7]), " ".join(self.provider[7:9])]))
        y -= 20

        # Customer info according to which information is given
        self.canvas.setFont("Arial", 12)
        if self.customer[1] is None:
            if self.customer[2] is None:
                if self.customer[4] is None:
                    pass
                else:
                    self.canvas.drawString(50, y, self.customer[4])
                    y -= 20
            else:
                if self.customer[4]:
                    self.canvas.drawString(50, y, self.customer[4])
                    y -= 20
                if self.customer[3] == 0:
                    salutation = "Frau"
                elif self.customer[3] == 1:
                    salutation = "Herr"
                else:
                    salutation = ""
                self.canvas.drawString(50, y, salutation + self.customer[1])
                y -= 20
        else:
            if self.customer[4]:
                self.canvas.drawString(50, y, self.customer[4])
                y -= 20
            self.canvas.drawString(50, y, " ".join(self.customer[1:3]))
            y -= 20
        self.canvas.drawString(50, y, " ".join(self.customer[5:7]))
        y -= 20
        self.canvas.drawString(50, y, " ".join(self.customer[7:9]))
        y -= 80

        # Bill heading (containing 'keyword')
        self.canvas.setFont("ArialBd", 14)
        self.canvas.drawString(50, y, self.bill[6])
        y -= 20

        # Bill id
        self.canvas.setFont("Arial", 10)
        self.canvas.drawString(50, y, f"Rechnungs-Nr.: {self.bill[5]}-{self.bill[0]:03d}")
        y -= 40

        # Customer greeting (according to gender)
        self.canvas.setFont("Arial", 12)
        greeting = "Sehr geehrte"
        if not self.customer[2]:
            greeting += " Damen und Herren"
        elif int(self.customer[3]) == 0:  # !!! REMOVE WITH NEW VERSION
            greeting += " Frau "+self.customer[2]
        elif int(self.customer[3]) == 1:
            greeting += "r Herr "+self.customer[2]
        elif int(self.customer[3]) == 2:
            greeting += ":r "+" ".join(self.customer[1:3])
        greeting += ","
        self.canvas.drawString(50, y, greeting)
        y -= 20
        self.canvas.drawString(50, y, "ich berechne folgende Leistungen:")
        y -= 30

        # Services
        self.canvas.setFont("Arial", 11)

        i = 0
        while i < len(self.services):
            if y > 250:
                self.canvas.drawString(60, y, " ".join([self.services[i][2], ".".join(map(str, self.services[i][5:8]))]))
                self.canvas.drawRightString(400, y, "{:.2f} €".format(self.services[i][3]).replace(".", ","))
                y -= 18
                if self.services[i][4]:
                    self.canvas.drawRightString(400, y, "+ {:.2f} €".format(self.services[i][4]).replace(".", ","))
                    y -= 18
                i += 1
            else:
                y = 700
                self.canvas.line(50, 80, 545.27, 80)
                self.canvas.setFont("ArialBd", 12)
                self.canvas.drawString(60, 60, "Bankverbindung")
                self.canvas.drawString(270, 60, "Kontakt")
                self.canvas.setFont("Arial", 8)
                self.canvas.drawString(60, 45, "IBAN: " + self.provider[11])
                self.canvas.drawString(60, 35, "BIC: " + self.provider[12])
                self.canvas.drawString(60, 25, "St-IdNr: " + self.provider[1])

                self.canvas.drawString(270, 45, "Tel.: " + self.provider[9])
                self.canvas.drawString(270, 35, "Mail : " + self.provider[10])

                if self.provider[13]:
                    self.canvas.drawString(270, 25, "Web: " + self.provider[13])
                    qrcode = qr.QrCode(self.provider[13])
                    qrcode.height = 60
                    qrcode.width = 60
                    qrcode.drawOn(self.canvas, 475.27, 20)
                self.canvas.showPage()
            pass
        self.canvas.setFont("ArialBd", 12)
        self.canvas.drawString(60, y, "Summe:")
        self.canvas.drawRightString(400, y, "{:.2f} €".format(sum([self.services[i][3] + self.services[i][4] for i in range(len(self.services))])).replace(".", ","))
        y -= 40
        self.canvas.setFont("Arial", 12)
        self.canvas.drawString(50, y, self.bill[7])
        y -= 40
        self.canvas.setFont("Arial", 10)
        if self.bill[8]:
            self.canvas.drawString(50, y, "Hinweis: Als Kleinunternehmer im Sinne von § 19 Abs. 1 UStG wird Umsatzsteuer nicht berechnet.")
            y -= 40
        if not self.bill[9]:
            self.canvas.setFont("ArialBd", 14)
            self.canvas.drawString(50, y, "Diese Rechnung ist ungültig.")
            y -= 20
        if self.bill[10]:
            self.canvas.setFont("ArialBd", 14)
            self.canvas.drawString(50, y, "Diese Rechnung ist bereits bezahlt.")

        self.canvas.line(50, 80, 545.27, 80)
        self.canvas.setFont("ArialBd", 12)
        self.canvas.drawString(60, 60, "Bankverbindung")
        self.canvas.drawString(270, 60, "Kontakt")
        self.canvas.setFont("Arial", 8)
        self.canvas.drawString(60, 45, "IBAN: "+ self.provider[11])
        self.canvas.drawString(60, 35, "BIC: "+ self.provider[12])
        self.canvas.drawString(60, 25, "St-IdNr: "+ self.provider[1])

        self.canvas.drawString(270, 45, "Tel.: " + self.provider[9])
        self.canvas.drawString(270, 35, "Mail : " + self.provider[10])

        if self.provider[13]:
            self.canvas.drawString(270, 25, "Web: " + self.provider[13])
            qrcode = qr.QrCode(self.provider[13])
            qrcode.height = 60
            qrcode.width = 60
            qrcode.drawOn(self.canvas, 475.27, 20)


        self.canvas.showPage()
        self.canvas.save()

class BillOverview:
    """Bill overview PDF Creator Class"""
    def __init__(self, bills, begin_date, end_date, provider, direction):
        self.bills = bills
        self.begin_date = begin_date
        self.end_date = end_date
        self.provider = provider

        self.canvas = canvas.Canvas(direction)

        pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
        pdfmetrics.registerFont(TTFont('ArialBd', 'ArialBd.ttf'))

    def save(self):
        """Saves PDF file. Has to be called separately after initialising the instance."""

        y = 750 # cursor for further body elements

        # Heading
        self.canvas.setFont("ArialBd", 14)
        self.canvas.drawString(50, y, "Rechnungsübersicht")
        y -= 50
        self.canvas.setFont("Arial", 12)
        self.canvas.drawString(50, y, "Zeitraum: "+".".join(self.begin_date)+" - "+".".join(self.end_date))
        y -= 50
        self.canvas.setFont("Arial", 8)
        i = 0
        while i < len(self.bills):
            if y > 250:
                self.canvas.drawString(50, y, f"R.-Nr.: {self.bills[i][7]}-{self.bills[i][3]:03d}")
                self.canvas.drawString(120, y, self.bills[i][4])
                self.canvas.drawString(300, y, " ".join([self.bills[i][2], self.bills[i][0], self.bills[i][1]]))
                self.canvas.drawRightString(550, y, "{:.2f} €".format(self.bills[i][8]+self.bills[i][9]).replace(".", ","))
                y -= 18
                i += 1
            else:
                y = 700
                self.canvas.line(50, 80, 545.27, 80)
                self.canvas.setFont("ArialBd", 12)
                self.canvas.drawString(60, 60, "Bankverbindung")
                self.canvas.drawString(270, 60, "Kontakt")
                self.canvas.setFont("Arial", 8)
                self.canvas.drawString(60, 45, "IBAN: " + self.provider[11])
                self.canvas.drawString(60, 35, "BIC: " + self.provider[12])
                self.canvas.drawString(60, 25, "St-IdNr: " + self.provider[1])

                self.canvas.drawString(270, 45, "Tel.: " + self.provider[9])
                self.canvas.drawString(270, 35, "Mail : " + self.provider[10])

                if self.provider[13]:
                    self.canvas.drawString(270, 25, "Web: " + self.provider[13])
                    qrcode = qr.QrCode(self.provider[13])
                    qrcode.height = 60
                    qrcode.width = 60
                    qrcode.drawOn(self.canvas, 475.27, 20)
                self.canvas.showPage()
            pass
        self.canvas.setFont("ArialBd", 12)
        self.canvas.drawString(60, y, "Summe:")
        self.canvas.drawRightString(550, y, "{:.2f} €".format(sum([self.bills[i][8] + self.bills[i][9] for i in range(len(self.bills))])).replace(".", ","))
        y -= 40

        self.canvas.line(50, 80, 545.27, 80)
        self.canvas.setFont("ArialBd", 12)
        self.canvas.drawString(60, 60, "Bankverbindung")
        self.canvas.drawString(270, 60, "Kontakt")
        self.canvas.setFont("Arial", 8)
        self.canvas.drawString(60, 45, "IBAN: "+ self.provider[11])
        self.canvas.drawString(60, 35, "BIC: "+ self.provider[12])
        self.canvas.drawString(60, 25, "St-IdNr: "+ self.provider[1])

        self.canvas.drawString(270, 45, "Tel.: " + self.provider[9])
        self.canvas.drawString(270, 35, "Mail : " + self.provider[10])

        if self.provider[13]:
            self.canvas.drawString(270, 25, "Web: " + self.provider[13])
            qrcode = qr.QrCode(self.provider[13])
            qrcode.height = 60
            qrcode.width = 60
            qrcode.drawOn(self.canvas, 475.27, 20)


        self.canvas.showPage()
        self.canvas.save()
from fpdf import FPDF, XPos, YPos

def calculate_income(nsj, deposit, tax_rate, cashback_rate):
    years = [1, 2, 3, 4, 5]
    deposit_rates = [21.6, 18.5, 12.5, 8, 5]  # Процентные ставки для вклада
    tax_deduction = 39000  # Налоговый вычет

    results = []
    for year, rate in zip(years, deposit_rates):
        deposit_income = deposit * (rate / 100) * (1 - tax_rate)
        nsj_income = nsj * (cashback_rate / 100) * (1 - tax_rate) + tax_deduction
        total_income = deposit_income + nsj_income
        results.append((year, deposit_income, nsj_income, total_income))

    # Сравнение с полным вкладом
    full_deposit_income = []
    total_portfolio = nsj + deposit
    for year, rate in zip(years, deposit_rates):
        income = total_portfolio * (rate / 100) * (1 - tax_rate)
        full_deposit_income.append(income)

    comparison = {
        "split_income": sum([res[3] for res in results]),
        "full_deposit_income": sum(full_deposit_income),
        "difference": sum([res[3] for res in results]) - sum(full_deposit_income)
    }

    return results, comparison

def generate_pdf(data, comparison):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf')  # Подключаем шрифт с поддержкой Unicode
    pdf.set_font('DejaVu', '', 12)

    pdf.cell(200, 10, text="Расчет доходности", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(200, 10, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font('DejaVu', '', 10)
    pdf.cell(40, 10, "Год", border=1)
    pdf.cell(50, 10, "Доход от вклада", border=1)
    pdf.cell(50, 10, "Доход от НСЖ", border=1)
    pdf.cell(50, 10, "Общий доход", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for year, deposit_income, nsj_income, total_income in data:
        pdf.cell(40, 10, str(year), border=1)
        pdf.cell(50, 10, f"{deposit_income:.2f}", border=1)
        pdf.cell(50, 10, f"{nsj_income:.2f}", border=1)
        pdf.cell(50, 10, f"{total_income:.2f}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.cell(200, 10, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, text="Сравнение доходов", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")

    pdf.set_font('DejaVu', '', 10)
    pdf.cell(100, 10, "Доход от всей суммы на вкладе", border=1)
    pdf.cell(100, 10, f"{comparison['full_deposit_income']:.2f} руб.", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.cell(100, 10, "Доход при разделении на вклад и НСЖ", border=1)
    pdf.cell(100, 10, f"{comparison['split_income']:.2f} руб.", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.cell(200, 10, text="", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(100, 10, "Разница между доходами", border=1)
    pdf.cell(100, 10, f"{comparison['difference']:.2f} руб.", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Сохранение PDF
    file_path = "income_report.pdf"
    pdf.output(file_path)
    return file_path

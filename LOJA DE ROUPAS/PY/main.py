from PyQt5 import uic, QtWidgets
import sqlite3
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import locale
import datetime
from datetime import date
import os

locale.setlocale(locale.LC_MONETARY, 'pt_BR.UTF-8')

# abrir telas

def salvar_estq():
    try:
        modelo = inicio.lineEdit.text()
        cor = inicio.lineEdit_2.text()
        valor_custo = ("{:.2f}".format(float(inicio.lineEdit_3.text().replace(",", "."))))
        valor_atacado = ("{:.2f}".format(float(inicio.lineEdit_4.text().replace(",", "."))))
        valor_varejo = ("{:.2f}".format(float(inicio.lineEdit_5.text().replace(",", "."))))
        obs = inicio.lineEdit_6.text()
        data = inicio.dateEdit.text()
        qtd = inicio.spinBox.text()
        print(valor_custo, valor_atacado, valor_varejo, qtd)

        if modelo=="":
            inicio.label_18.setText("Itens vazios!")
            inicio.label_17.setText("")
        elif valor_custo=="":
            inicio.label_18.setText("Itens vazios!")
            inicio.label_17.setText("")

        else:

            try:
                banco = sqlite3.connect('DB/estoque.db')
                cursor = banco.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS dados ( modelo text, cor text, qtd float, valor_custo float, valor_atacado float, valor_varejo float, data date, obs text)")
                cursor.execute("INSERT INTO dados VALUES ('"+modelo+"','"+cor+"','"+qtd+"','"+valor_custo+"','"+valor_atacado+"','"+valor_varejo+"','"+data+"','"+obs+"')")
                banco.commit()
                banco.close()
                inicio.lineEdit.setText("")
                inicio.lineEdit_2.setText("")
                inicio.lineEdit_3.setText("")
                inicio.lineEdit_4.setText("")
                inicio.lineEdit_5.setText("")
                inicio.lineEdit_6.setText("")
                inicio.spinBox.clear()
                inicio.dateEdit.setDate(datetime.date.today())
                inicio.label_17.setText("Peça incluida com sucesso!")
                inicio.label_18.setText("")
            except sqlite3.Error as erro:
                print("Erro ao inserir os dados: ",erro)

    except:
            inicio.label_18.setText("Itens vazios!")

def listar_estq():
    estoque.show()
    banco = sqlite3.connect('DB/estoque.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM dados")
    dados_lidos = cursor.fetchall()
    estoque.tableWidget.setRowCount(len(dados_lidos))
    estoque.tableWidget.setColumnWidth(0,276)
    estoque.tableWidget.setColumnWidth(1, 150)
    estoque.tableWidget.setColumnWidth(2, 150)
    estoque.tableWidget.setColumnWidth(3, 150)
    estoque.tableWidget.setColumnWidth(4, 145)
    estoque.tableWidget.setColumnWidth(5, 145)
    estoque.tableWidget.setColumnWidth(6, 150)
    estoque.tableWidget.setColumnWidth(7, 150)

    for i in range (0,len(dados_lidos)):
        for j in range (0,8):
            estoque.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))
            estoque.tableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(str(locale.currency((float(dados_lidos[i][3])), grouping=True))))
            estoque.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(locale.currency((float(dados_lidos[i][4])), grouping=True))))
            estoque.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(str(locale.currency((float(dados_lidos[i][5])), grouping=True))))

    banco = sqlite3.connect('DB/estoque.db')
    cursor = banco.cursor()
    sql = f"SELECT SUM(valor_custo*qtd) FROM dados"
    cursor.execute(sql)
    sum = cursor.fetchall()
    if str(sum) == "[(None,)]":
        estoque.label_3.setText("0")
    else:
        estoque.label_3.setText((locale.currency(float(sum[0][0]), grouping=True)))

def abrir_venda():
    venda.show()
    venda.spinBox_2.setValue(0)
    venda.spinBox.setValue(0)
    venda.dateEdit.setDate(datetime.date.today())
    linha = estoque.tableWidget.currentRow()
    banco = sqlite3.connect('DB/estoque.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM dados")
    dados_lidos = cursor.fetchall()
    id = dados_lidos[linha][0]
    id2 = dados_lidos[linha][1]
    cursor.execute("SELECT * FROM dados WHERE modelo='" + id + "' and cor='"+id2+"'")
    edit = cursor.fetchall()

    venda.lineEdit.setText(str(edit[0][0]))
    venda.lineEdit_2.setText(str(edit[0][1]))
    venda.lineEdit_3.setText(str(edit[0][2]))
    venda.lineEdit_4.setText(str(edit[0][3]))
    venda.lineEdit_5.setText(str(edit[0][4]))
    venda.lineEdit_6.setText(str(edit[0][5]))
    qe = (float(venda.lineEdit_3.text()))
    venda.spinBox_2.setMaximum(qe)

def alterar_valor():

    va = (float(venda.lineEdit_5.text()))
    vj = (float(venda.lineEdit_6.text()))
    q = (float(venda.spinBox_2.text()))
    d = (float(venda.spinBox.text()))

    if venda.radioButton.isChecked():
        valor = va

    elif venda.radioButton_2.isChecked():
        valor = vj

    else:
        valor = 0

    v = valor * q
    dd = v * d / 100
    vv = v - dd
    venda.lineEdit_8.setText(str("{:.2f}".format(dd)))
    venda.lineEdit_9.setText(str("{:.2f}".format(vv)))
    venda.lineEdit_11.setText(str("{:.2f}".format(v)))

def vender():
    qe = (float(venda.lineEdit_3.text()))
    q = (float(venda.spinBox_2.text()))
    md = venda.lineEdit.text()
    cor = venda.lineEdit_2.text()
    qtd = venda.spinBox_2.text()
    cliente = venda.lineEdit_10.text()
    vv = venda.lineEdit_9.text()
    vlr = venda.lineEdit_4.text()
    data = datetime.datetime.strptime(venda.dateEdit.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
    lucro = "{:.2f}".format((float(vv))-(float(vlr)*q))

    if venda.radioButton.isChecked():
        tipo = "Atacado"

    elif venda.radioButton_2.isChecked():
        tipo = "Varejo"

    else:
        tipo = "Não selecionado"
    try:
        banco = sqlite3.connect('DB/relatorio.db')
        cursor = banco.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS dados (md text, cor text, qtd integer, cliente text, lucro numeric, data date, tipo text)")
        cursor.execute(
            "INSERT INTO dados VALUES ('"+md+"','"+cor+"','"+qtd+"','"+cliente+"','"+(str(lucro))+"','"+data+"','"+tipo+"')")
        banco.commit()
        banco.close()

        venda.lineEdit_10.setText("")
        venda.lineEdit_11.setText("")
        venda.spinBox_2.clear()
        venda.spinBox.clear()
        venda.lineEdit_8.setText("")
        venda.lineEdit_9.setText("")


    except sqlite3.Error as erro:
        print("Erro ao inserir os dados: ", erro)

    dl = venda.lineEdit.text()
    dl2 = venda.lineEdit_2.text()
    if qe-q==0:

        try:
            banco = sqlite3.connect('DB/estoque.db')
            cursor = banco.cursor()
            cursor.execute("DELETE from dados WHERE modelo='"+dl+"' and cor='"+dl2+"'")
            banco.commit()
            banco.close()

        except sqlite3.Error as erro:
            print("Erro ao excluir os dados: ", erro)
    else:
        qn=qe-q
        try:
            banco = sqlite3.connect('DB/estoque.db')
            cursor = banco.cursor()
            cursor.execute("UPDATE dados SET qtd='"+(str(qn))+"' WHERE modelo='"+dl+"' and cor='"+dl2+"'")
            banco.commit()
            banco.close()

        except sqlite3.Error as erro:
            print("Erro ao excluir os dados: ", erro)

    venda.close()

def atualizar ():
    adicionar.show()
    linha = estoque.tableWidget.currentRow()
    banco = sqlite3.connect('DB/estoque.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM dados")
    dados_lidos = cursor.fetchall()
    id = dados_lidos[linha][0]
    id2 = dados_lidos[linha][1]
    adicionar.label.setText(id)
    adicionar.label_2.setText(id2)
    adicionar.label_3.setText(str(dados_lidos[linha][2]))

def adc():

    banco = sqlite3.connect('DB/estoque.db')
    cursor = banco.cursor()
    cursor.execute("SELECT * FROM dados")
    id = adicionar.label.text()
    id2 = adicionar.label_2.text()
    q2 = float(adicionar.spinBox.text())
    q1 = float(adicionar.label_3.text())
    q3 = q1+q2
    cursor.execute("UPDATE dados SET qtd= '"+(str(q3))+"'  WHERE modelo='" + id + "' and cor='" + id2 + "'")
    banco.commit()
    banco.close()
    adicionar.close()


def relatorio_abrir():
        relatorio.show()
        banco = sqlite3.connect('DB/relatorio.db')
        cursor = banco.cursor()
        cursor.execute("SELECT * FROM dados")
        dados_lidos = cursor.fetchall()
        relatorio.tableWidget.setRowCount(len(dados_lidos))
        relatorio.tableWidget.setColumnWidth(0, 270)
        relatorio.tableWidget.setColumnWidth(1, 125)
        relatorio.tableWidget.setColumnWidth(2, 110)
        relatorio.tableWidget.setColumnWidth(3, 110)
        relatorio.tableWidget.setColumnWidth(4, 110)
        relatorio.tableWidget.setColumnWidth(5, 150)
        relatorio.tableWidget.setColumnWidth(6, 110)


        for i in range(0, len(dados_lidos)):

            for j in range(0, 7):
                relatorio.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))
                relatorio.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(locale.currency((float(dados_lidos[i][4])), grouping=True))))
                relatorio.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(str(datetime.datetime.strptime((dados_lidos[i][5]), "%Y-%m-%d").strftime("%d/%m/%Y"))))

        banco = sqlite3.connect('DB/relatorio.db')
        cursor = banco.cursor()
        sql = f"SELECT SUM(lucro) FROM dados"
        cursor.execute(sql)
        sum = cursor.fetchall()
        if str(sum) == "[(None,)]":
            relatorio.label_2.setText("0")
        else:
            relatorio.label_2.setText((locale.currency(float(sum[0][0]), grouping=True)))

def filtro():

    if relatorio.tableWidget.rowCount()>0:
        relatorio.tableWidget.clearContents()

    relatorio.show()
    datainicio = datetime.datetime.strptime(relatorio.dateEdit.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
    datafinal = datetime.datetime.strptime(relatorio.dateEdit_2.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
    banco = sqlite3.connect('DB/relatorio.db')
    cursor = banco.cursor()
    sql = f"SELECT * FROM dados WHERE data between '{datainicio}' and '{datafinal}'"
    cursor.execute(sql)
    dados_lidos = cursor.fetchall()

    for i in range(0, len(dados_lidos)):
        for j in range(0, 7):
            relatorio.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))
            relatorio.tableWidget.setItem(i, 4, QtWidgets.QTableWidgetItem(str(locale.currency((float(dados_lidos[i][4])), grouping=True))))
            relatorio.tableWidget.setItem(i, 5, QtWidgets.QTableWidgetItem(str(datetime.datetime.strptime((dados_lidos[i][5]), "%Y-%m-%d").strftime("%d/%m/%Y"))))


    banco = sqlite3.connect('DB/relatorio.db')
    cursor = banco.cursor()
    sql = f"SELECT SUM(lucro) FROM dados WHERE data between '{datainicio}' and '{datafinal}'"
    cursor.execute(sql)
    sum = cursor.fetchall()
    if str(sum)=="[(None,)]":
        relatorio.label_2.setText("0")
    else:
        relatorio.label_2.setText((locale.currency(float(sum[0][0]), grouping=True)))

def gerar_pdf():
    try:
        banco = sqlite3.connect('DB/estoque.db')
        cursor = banco.cursor()
        cursor.execute("SELECT * FROM dados")
        dados_lidos = cursor.fetchall()
        y = 0

        pdf = canvas.Canvas("RELATORIOS/Estoque.pdf", pagesize=A4)
        pdf.setFont("Helvetica-Bold",16)
        pdf.drawImage('SCR/icn.png',0,810,width=100, height=30)
        pdf.drawString(253,820, "ESTOQUE")
        pdf.setFont("Helvetica-Bold",10)
        pdf.drawString(10,793,"MODELO")
        pdf.drawString(150, 793, "COR")
        pdf.drawString(210, 793, "QTD")
        pdf.drawString(255, 793, "CUSTO")
        pdf.drawString(325, 793, "ATACADO")
        pdf.drawString(395, 793, "VAREJO")
        pdf.drawString(460, 793, "DATA")
        pdf.drawString(530, 793, "OBS")
        pdf.line(0,805,610,805)
        pdf.line(0, 790, 610, 790)


        for i in range(0, len(dados_lidos)):
            pdf.setFont("Helvetica", 10)
            y = y + 15
            pdf.drawString(10,793 - y, str(dados_lidos[i][0]))
            pdf.drawString(150, 793 - y, str(dados_lidos[i][1]))
            pdf.drawString(215, 793 - y, str(dados_lidos[i][2]))
            pdf.drawString(260, 793 - y, str(dados_lidos[i][3]))
            pdf.drawString(338, 793 - y, str(dados_lidos[i][4]))
            pdf.drawString(403, 793 - y, str(dados_lidos[i][5]))
            pdf.drawString(450, 793 - y, str(dados_lidos[i][6]))
            pdf.drawString(533, 793 - y, str(dados_lidos[i][7]))
            if (i>1) and (i%49==0):
                pdf.showPage()
                y=0
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawImage('SCR/icn.png',0,810,width=100, height=30)
                pdf.drawString(253, 820, "ESTOQUE")
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(10,793,"MODELO")
                pdf.drawString(150, 793, "COR")
                pdf.drawString(210, 793, "QTD")
                pdf.drawString(255, 793, "CUSTO")
                pdf.drawString(325, 793, "ATACADO")
                pdf.drawString(395, 793, "VAREJO")
                pdf.drawString(460, 793, "DATA")
                pdf.drawString(530, 793, "OBS")
                pdf.line(0,805,610,805)
                pdf.line(0, 790, 610, 790)
        pdf.save()

        path = 'RELATORIOS/Estoque.pdf'
        os.system(path)
    except sqlite3.Error as erro:
        print("Erro ao editar os dados: ",erro)

def gerar_pdf2():
    try:
        datainicio = datetime.datetime.strptime(relatorio.dateEdit.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
        datafinal = datetime.datetime.strptime(relatorio.dateEdit_2.text(), "%d/%m/%Y").strftime("%Y-%m-%d")
        banco = sqlite3.connect('DB/relatorio.db')
        cursor = banco.cursor()
        sql = f"SELECT * FROM dados WHERE data between '{datainicio}' and '{datafinal}'"
        cursor.execute(sql)
        dados_lidos = cursor.fetchall()
        periodo = relatorio.dateEdit.text() + " até " + relatorio.dateEdit_2.text()

        if str(dados_lidos) == "[]":
            banco = sqlite3.connect('DB/relatorio.db')
            cursor = banco.cursor()
            cursor.execute("SELECT * FROM dados")
            dados_lidos = cursor.fetchall()

            periodo = "2022-01-01 até " + str(date.today())
        y = 0

        pdf = canvas.Canvas("RELATORIOS/Relatorio.pdf", pagesize=A4)
        pdf.setFont("Helvetica-Bold",16)
        pdf.drawImage('SCR/icn.png',0,810,width=100, height=30)
        pdf.drawString(220,820, "RELATÓRIO DE VENDAS")
        pdf.setFont("Helvetica-Bold",10)
        pdf.drawString(10, 793, "MODELO")
        pdf.drawString(150,793,"COR")
        pdf.drawString(250, 793, "QTD")
        pdf.drawString(300, 793, "CLIENTE")
        pdf.drawString(383, 793, "LUCRO")
        pdf.drawString(466, 793, "DATA")
        pdf.drawString(550, 793, "TIPO")
        pdf.line(0,805,610,805)
        pdf.line(0, 790, 610, 790)


        for i in range(0, len(dados_lidos)):
            pdf.setFont("Helvetica", 10)
            y = y + 15
            pdf.drawString(10, 793 - y, str(dados_lidos[i][0]))
            pdf.drawString(150, 793 - y, str(dados_lidos[i][1]))
            pdf.drawString(250, 793 - y, str(dados_lidos[i][2]))
            pdf.drawString(300, 793 - y, str(dados_lidos[i][3]))
            pdf.drawString(383, 793 - y, str("{:.2f}".format(float(dados_lidos[i][4]))))
            pdf.drawString(466, 793 - y, str(dados_lidos[i][5]))
            pdf.drawString(550, 793 - y, str(dados_lidos[i][6]))

            if (i>1) and (i%30==0):
                pdf.showPage()
                y=0
                pdf.setFont("Helvetica-Bold", 16)
                pdf.drawImage('logo3.png', 10, 785, width=52, height=52)
                pdf.drawString(220, 820, "RELATÓRIO DE VENDAS")
                pdf.setFont("Helvetica-Bold", 14)
                pdf.drawString(270, 800, "TEE BRASIL")
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(10, 793, "MODELO")
                pdf.drawString(150,793,"COR")
                pdf.drawString(250, 793, "QTD")
                pdf.drawString(300, 793, "CLIENTE")
                pdf.drawString(383, 793, "LUCRO")
                pdf.drawString(466, 793, "DATA")
                pdf.drawString(550, 793, "TIPO")
                pdf.line(0,805,610,805)
                pdf.line(0, 790, 610, 790)

        pdf.line(5, 40, 830, 40)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(430, 15, "LUCRO:"+str(relatorio.label_2.text()))
        pdf.drawString(15, 15, "PERIODO:"+str(periodo))
        pdf.save()

        path = 'RELATORIOS/Relatorio.pdf'
        os.system(path)
    except sqlite3.Error as erro:
        print("Erro ao editar os dados: ",erro)

#converter QT em python
app=QtWidgets.QApplication([])
inicio = uic.loadUi("QT/inicio.ui")
estoque = uic.loadUi("QT/estoque.ui")
relatorio = uic.loadUi("QT/relatorio.ui")
venda = uic.loadUi("QT/venda.ui")
adicionar = uic.loadUi("QT/atualizar.ui")

inicio.incluir.clicked.connect(salvar_estq)
inicio.estoque.clicked.connect(listar_estq)
estoque.atualizar.clicked.connect(listar_estq)
inicio.relatorio.clicked.connect(relatorio_abrir)
estoque.vd.clicked.connect(abrir_venda)
estoque.at.clicked.connect(atualizar)
adicionar.pushButton.clicked.connect(adc)
venda.incld.clicked.connect(vender)
venda.spinBox.editingFinished.connect(alterar_valor)
venda.spinBox_2.editingFinished.connect(alterar_valor)
venda.radioButton.clicked.connect(alterar_valor)
venda.radioButton_2.clicked.connect(alterar_valor)
relatorio.filtro_2.clicked.connect(filtro)
relatorio.limpar.clicked.connect(relatorio_abrir)
estoque.excel.clicked.connect(gerar_pdf)
relatorio.imp.clicked.connect(gerar_pdf2)

inicio.show()
inicio.spinBox.setMinimum(1)
inicio.dateEdit.setDate(datetime.date.today())
app.exec()

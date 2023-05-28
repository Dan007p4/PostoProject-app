import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import streamlit_authenticator as stauth
import yaml
import xlrd
import mysql.connector
from yaml.loader import SafeLoader
from sqlalchemy import create_engine
import seaborn as sns
import matplotlib.pyplot as plt
import unidecode
st.set_page_config(page_icon="🏥", page_title="Gerenciador de dados")
##FAZENDO CONEXÃO COM O DB##

connection = mysql.connector.connect(
    host="aws.connect.psdb.cloud",
    user=st.secrets["db_username"],
    passwd=st.secrets["db_password"],
    # host="aws.connect.psdb.cloud",
    # user="12jdq52t7tmudf8y0bp7",
    # passwd="pscale_pw_cLEVkrzsQJvkFZQrswW7a4xaKLuDtu3Vx6e7hRqg2j2",
    db="database",
    ssl_ca="cacert-2023-01-10.pem"
    # ssl={
    #     "ca": "cacert-2023-01-10.pem"
    # }


)


# connection = MySQLdb.connect(
#     host="127.0.0.1", user="root", passwd="02041224dD", db="sex")
c = connection.cursor()

##FAZENDO TELA DE LOGIN##
with open('config.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Login', 'main')

##CRIANDO MENU##


def Clean_Names(name):
    name = unidecode.unidecode(name)
    name = name.replace(" ", '_')
    name = name.replace("/", '_')
    name = name.replace(".", '')

    return name


if (authentication_status == True) & (username == 'admistrador'):
    authenticator.logout('Logout', 'main')
    with st.sidebar:

        selected = option_menu(
            menu_title="Menu",
            options=["Gerenciador de dados",
                     "Manipulador de dados", "Analise de dados", "Subir tabelas"],
            menu_icon="border-width"
        )
    st.sidebar.image(
        "WhatsApp Image 2023-02-21 at 14.22.25 (1).png", use_column_width=True)

    # logo = st.image("rsz_1rsz_whatsapp_image_2023-02-21_at_142225_1.png")

    # height = 300
    # st.markdown(f"""<style>[data-testid="stSidebarNav"] {{background-image: {logo};background-repeat: no-repeat;padding-top: {height - 40}px;background-position: 20px 20px;}}</style>""",
    #             unsafe_allow_html=True,
    #             )

    if selected == "Gerenciador de dados":
        st.session_state.new_form2 = 0
        st.divider()
        st.title("Gerenciador de dados")

    if selected == "Manipulador de dados":

        ##CRIANDO VARIAVEIS DA SESSÃO DA ABA##
        if 'new_form' not in st.session_state:
            st.session_state['new_form'] = 0

        if 'new_form2' not in st.session_state:
            st.session_state['new_form2'] = 0

        if 'columns_number' not in st.session_state:
            st.session_state['columns_number'] = 0

        if 'tableName' not in st.session_state:
            st.session_state['tableName'] = 0

        if 'list_tablesofc' not in st.session_state:
            st.session_state['list_tablesofc'] = list_tablesofc = []

        if 'datau' not in st.session_state:
            st.session_state['datau'] = lista_datau = []

        ##PRIMEIRA TELA DA ABA##
        st.divider()
        st.title("Manipulador de dados")

        if st.session_state.columns_number > 0:
            st.session_state.new_form = st.session_state.columns_number

        if st.session_state.list_tablesofc != []:
            st.session_state.new_form2 = 1

        if st.session_state.new_form2 > 0:

            count = 0

            for i in st.session_state.list_tablesofc:
                count = count+1
                data = pd.read_sql("SELECT * FROM "+i, con=connection)
                st.session_state.datau.append(data)
                st.subheader(str(count)+"º tabelas selecionada")
                st.dataframe(data)

            conc = pd.concat(st.session_state.datau, axis=0)
            st.subheader("Tabela concatenada")
            st.dataframe(conc)

            from io import BytesIO
            import xlsxwriter
            from pyxlsb import open_workbook as open_xlsb

            def to_excel(df):
                output = BytesIO()
                writer = pd.ExcelWriter(output, engine='xlsxwriter')
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                format1 = workbook.add_format({'num_format': '0.00'})
                worksheet.set_column('A:A', None, format1)
                writer.save()
                processed_data = output.getvalue()
                return processed_data

            st.download_button(
                label="Fazer dowload da tabela concatenada",
                data=to_excel(conc),
                file_name='large_df.xlsx'
            )
            st.session_state.datau = []
            cancel_b = st.button("Cancelar")
            if cancel_b:
                st.session_state.datau = []

            st.session_state.new_form2 = 0

        elif st.session_state.new_form > 0:

            count = -1
            st.session_state.tableName = st.session_state.tableName
            st.write(st.session_state.tableName)
            st.session_state['list_columnsT'] = list_columnsT = []
            st.session_state['list_columnsN'] = list_columnsN = []

            for i in range(0, st.session_state.new_form):
                st.session_state.list_columnsN.append(str(i))
                st.session_state.list_columnsT.append(str(i))

            for i in st.session_state.list_columnsN:
                count = count+1
                count_str = int(i)+1
                list_columnsN[count] = st.text_input(
                    "Insira o nome da "+str(count_str)+"º coluna")

                list_columnsT[count] = st.selectbox(
                    "Selecione o tipo da "+str(count_str)+"º coluna", ('Numerico', 'Categorico', 'Data'))

            for i in range(0, int(len(st.session_state.list_columnsT))):
                if list_columnsT[i] == 'Numerico':
                    list_columnsT[i] = list_columnsT[i].replace(
                        'Numerico', 'int')

                if list_columnsT[i] == 'Categorico':
                    list_columnsT[i] = list_columnsT[i].replace(
                        'Categorico', 'varchar(150)')

                if list_columnsT[i] == 'Data':
                    list_columnsT[i] = list_columnsT[i].replace('Data', 'date')

            create = st.button("Criar")
            cancel_b = st.button("Cancelar")
            if cancel_b:
                st.session_state.new_form = 0

            if create:
                create_command = "CREATE TABLE " + \
                    Clean_Names(str(st.session_state.tableName))+" ("

                for i in range(0, int(len(st.session_state.list_columnsN))):
                    if list_columnsN[i] == list_columnsN[-1]:
                        create_command = create_command + \
                            Clean_Names(str(list_columnsN[i]))+" " + \
                            Clean_Names(str(list_columnsT[i]))+");"
                    else:
                        create_command = create_command + \
                            Clean_Names(str(list_columnsN[i])) + " " + \
                            Clean_Names(str(list_columnsT[i]))+","
                st.write(create_command)
                st.write("Criado com sucesso!")
                c.execute(create_command)
                count = -1
                st.session_state.new_form = 0

        ##SEGUNDA TELA DA ABA##
        else:
            ##CONCATENAÇÃO DE TABELAS##
            new_concat = st.button("Criar concatenação")
            if new_concat:
                with st.form(key='concat_columns'):
                    c.execute(
                        "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'database';")
                    list_tables = []

                    tables = c.fetchall()
                    for i in tables:
                        value = i[2]
                        list_tables.append(value)

                    list_tablesofc = st.multiselect('Escolha as tabelas a serem concatenadas',
                                                    list_tables, key='list_tablesofc')

                    submitted = st.form_submit_button(label="Enviar")
                    if submitted:
                        st.dataframe(dados, key="concat_columns")
                st.button("Cancelar")

            ##CRIANDO NOVO TIPO DE TABELA##
            new_table = st.button("Criar novo tipo de tabela")
            if new_table:
                if st.session_state.new_form == 0:

                    with st.form(key='number_columns'):
                        columnsName = st.text_input(
                            "Insira o nome da nova tabela", key='tableName')
                        columnsN = st.number_input(
                            "Insira a quntidade de colunas", min_value=0, max_value=30, key='columns_number')

                        submitted = st.form_submit_button(label="Enviar")
                    st.button("Cancelar")

    if selected == "Analise de dados":
        st.divider()
        st.title("Analise de dados")
        with st.form(key='concat_columns'):
            c.execute(
                "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'database';")
            list_tables = []
            list_features = []
            list_chart = ["Grafico de barras", "Grafico de linha"]

            list_chartfunc = ["Contar",
                              "Comparar"]

            tables = c.fetchall()

            for i in tables:
                value = i[2]
                if ((('tipo' in value) | ('TIPO' in value)) & (('1' in value) | ('2' in value) | ('3' in value) | ('4' in value) | ('5' in value) | ('6' in value) | ('7' in value) | ('8' in value) | ('9' in value))):
                    list_tables.append(value)

        list_tablesofc = st.selectbox('Escolha as tabelas a serem analisadas',
                                      list_tables)
        c.execute(
            "SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where table_schema = 'database' and table_name = '" + str(list_tablesofc)+"';")
        columns = c.fetchall()

        for i in columns:
            value = i[0]
            list_features.append(value)

        type_columns = st.multiselect('Escolha as colunas a serem analisadas',
                                      list_features)

        type_chart = st.selectbox('Escolha os tipos do grafico',
                                  list_chart)

        # func_chart = st.selectbox('Escolha a função do grafico',
        #                           list_chartfunc)

        if (list_tablesofc != None) & (type_columns != []) & (list_tablesofc != None):
            data = pd.read_sql("SELECT * FROM "+list_tablesofc, con=connection)
            st.dataframe(data)
            fig = plt.figure(figsize=(12, 9))

            if type_chart == "Grafico de barras":
                sns.countplot(x=data[str(type_columns[0])])
                st.pyplot(fig)

            # if type_chart == "Grafico de pizza":
            #     sns.pieplot(x=data[str(type_columns[0])])
            #     st.pyplot(fig)

            if type_chart == "Grafico de linha":
                sns.lineplot(data=data, x=data[str(type_columns[0])],
                             y=data[str(type_columns[1])])
                st.pyplot(fig)

            st.session_state.new_form2 = 0

        # dados = st.file_uploader("Tabela", type=["xlsx"])
        # dados = pd.read_excel(dados, sheet_name='BASE DE DADOS')
        # dados = dados.drop([0, 1, 2, 3, 4], axis=0)
        # dados.columns = dados.iloc[0].values
        # dados = dados.drop(5, axis=0)
        # dados = dados.reset_index()
        # dados = dados.drop('index', axis=1)
        # st.bar_chart(dados['QNT'])
        # st.ploty_chart(dados['GENERO'])

    if selected == "Subir tabelas":
        st.session_state.new_form2 = 0
        st.divider()
        st.title("Insira sua tabela e as informações necessarias abaixo")
        c.execute(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'database';")
        list_tables = []

        tables = c.fetchall()
        for i in tables:
            value = i[2]
            if (('TIPO' in value) & ('1' not in value) & ('2' not in value) and ('3' not in value) and ('4' not in value) and ('5' not in value) and ('6' not in value) and ('7' not in value) and ('8' not in value) and ('9' not in value)) | (('tipo' in value) & ('1' not in value) & ('1' not in value) & ('2' not in value) and ('3' not in value) and ('4' not in value) and ('5' not in value) and ('6' not in value) and ('7' not in value) and ('8' not in value) and ('9' not in value)):
                list_tables.append(value)

        selection_type = st.selectbox("Selecione o tipo da tabela",
                                      list_tables)

        # c.execute(
        #     "SELECT count(*) FROM information_schema.columns WHERE table_name ='"+selection_type + "';")
        # number_len = c.fetchall()

        st.subheader(
            ":red[Clique no botão 'Browse files'a baixo para subir a tabela ⇩]")

        c.execute("SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where table_schema = 'database' and table_name = '"+selection_type+"'")
        columns = c.fetchall()
        dados4 = st.file_uploader("Tabela", type=["xlsx"])

        if (dados4 != None) & (selection_type == "TIPO_POSTO_PADRAO"):
            dados4 = pd.read_excel(
                dados4, sheet_name='BASE DE DADOS', engine='openpyxl')
            dados4 = dados4.drop([0, 1, 2, 3, 4], axis=0)
            dados4.columns = dados4.iloc[0].values
            dados4 = dados4.drop(5, axis=0)
            dados4 = dados4.reset_index()
            dados4 = dados4.drop('index', axis=1)
            for i in dados4.columns:
                dados4 = dados4.rename({i: Clean_Names(i)}, axis=1)

            number_columns_verify = []
            for i in dados4.columns:
                for x in columns:
                    if i in x:
                        number_columns_verify.append(x)

            if(dados4.shape[1] == len(columns)) & (len(number_columns_verify) == dados4.shape[1]):

                # if dados4.shape[1] != number_len:
                #     st.write("Tipo errado")
                # st.write(dados4.shape[1])
                # st.write(number_len)

                st.dataframe(dados4)
                name = st.text_input("Nome da unidade")
                date = st.text_input("Data do envio da tabela")
                nameFinal = name+date+str(selection_type)

                ssl_args = {'ssl': "cacert-2023-01-10.pem"}

                engine = create_engine(
                    'mysql+mysqldb://'+st.secrets["db_username"]+':'+st.secrets["db_password"]+'@aws.connect.psdb.cloud/database', connect_args=ssl_args)
                # engine = create_engine(
                #     'mysql+mysqldb://root:02041224dD@127.0.0.1/sex')
                send_table = st.button("Enviar Tabela")
                if send_table:
                    dados4.to_sql(nameFinal, con=engine,
                                  if_exists='replace', index=False)
                    st.write("Tabela enviada com sucesso!")
            else:
                st.warning("Tipo não compatível")

        elif (dados4 != None):

            for i in dados4.columns:
                dados4 = dados4.rename({i: Clean_Names(i)}, axis=1)

            dados4 = pd.read_excel(dados4)

            number_columns_verify = []
            for i in dados4.columns:
                for x in columns:
                    if i in x:
                        number_columns_verify.append(x)

            if(dados4.shape[1] == len(columns)) & (len(number_columns_verify) == dados4.shape[1]):

                # if dados4.shape[1] != number_len:
                #     st.write("Tipo errado")
                # st.write(dados4.shape[1])
                # st.write(number_len)

                st.dataframe(dados4)
                name = st.text_input("Nome da unidade")
                date = st.text_input("Data do envio da tabela")
                nameFinal = name+date+str(selection_type)

                ssl_args = {'ssl': "cacert-2023-01-10.pem"}

                engine = create_engine(
                    'mysql+mysqldb://'+st.secrets["db_username"]+':'+st.secrets["db_password"]+'@aws.connect.psdb.cloud/database', connect_args=ssl_args)
                # engine = create_engine(
                #     'mysql+mysqldb://root:02041224dD@127.0.0.1/sex')
                send_table = st.button("Enviar Tabela")
                if send_table:
                    dados4.to_sql(nameFinal, con=engine,
                                  if_exists='replace', index=False)
            else:
                st.error("Tipo não compatível")


elif (authentication_status == True) & (username == 'usuario'):
    authenticator.logout('Logout', 'main')
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Subir tabelas"],
            menu_icon="border-width"
        )
        st.sidebar.image(
            "WhatsApp Image 2023-02-21 at 14.22.25 (1).jpeg", use_column_width=True)
    if 'new_form2' not in st.session_state:
        st.session_state['new_form2'] = 0

    if selected == "Subir tabelas":
        st.session_state.new_form2 = 0
        st.divider()
        st.title("Insira sua tabela e as informações necessarias abaixo")
        c.execute(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'database';")
        list_tables = []

        tables = c.fetchall()
        for i in tables:
            value = i[2]
            if(('TIPO' in value) & ('1' not in value) & ('2' not in value) and ('3' not in value) and ('4' not in value) and ('5' not in value) and ('6' not in value) and ('7' not in value) and ('8' not in value) and ('9' not in value)) | (('tipo' in value) & ('1' not in value) & ('1' not in value) & ('2' not in value) and ('3' not in value) and ('4' not in value) and ('5' not in value) and ('6' not in value) and ('7' not in value) and ('8' not in value) and ('9' not in value)):

                list_tables.append(value)

        selection_type = st.selectbox("Selecione o tipo da tabela",
                                      list_tables)

        # c.execute(
        #     "SELECT count(*) FROM information_schema.columns WHERE table_name ='"+selection_type + "';")
        # number_len = c.fetchall()

        st.subheader(
            ":red[Clique no botão 'Browse files'a baixo para subir a tabela ⇩]")

        c.execute("SELECT COLUMN_NAME from INFORMATION_SCHEMA.COLUMNS where table_schema = 'database' and table_name = '"+selection_type+"'")
        columns = c.fetchall()
        dados4 = st.file_uploader("Tabela", type=["xlsx"])

        if (dados4 != None) & (selection_type == "TIPO_POSTO_PADRAO"):
            dados4 = pd.read_excel(
                dados4, sheet_name='BASE DE DADOS', engine='openpyxl')
            dados4 = dados4.drop([0, 1, 2, 3, 4], axis=0)
            dados4.columns = dados4.iloc[0].values
            dados4 = dados4.drop(5, axis=0)
            dados4 = dados4.reset_index()
            dados4 = dados4.drop('index', axis=1)
            for i in dados4.columns:
                dados4 = dados4.rename({i: Clean_Names(i)}, axis=1)

            number_columns_verify = []
            for i in dados4.columns:
                for x in columns:
                    if i in x:
                        number_columns_verify.append(x)

            if(dados4.shape[1] == len(columns)) & (len(number_columns_verify) == dados4.shape[1]):

                # if dados4.shape[1] != number_len:
                #     st.write("Tipo errado")
                # st.write(dados4.shape[1])
                # st.write(number_len)

                st.dataframe(dados4)
                name = st.text_input("Nome da unidade")
                date = st.text_input("Data do envio da tabela")
                nameFinal = name+date+str(selection_type)

                ssl_args = {'ssl': "cacert-2023-01-10.pem"}

                engine = create_engine(
                    'mysql+mysqldb://'+st.secrets["db_username"]+':'+st.secrets["db_password"]+'@aws.connect.psdb.cloud/database', connect_args=ssl_args)
                # engine = create_engine(
                #     'mysql+mysqldb://root:02041224dD@127.0.0.1/sex')
                send_table = st.button("Enviar Tabela")
                if send_table:
                    dados4.to_sql(nameFinal, con=engine,
                                  if_exists='replace', index=False)
                    st.write("Tabela enviada com sucesso!")
            else:
                st.warning("Tipo não compatível")

        elif (dados4 != None):

            for i in dados4.columns:
                dados4 = dados4.rename({i: Clean_Names(i)}, axis=1)

            dados4 = pd.read_excel(dados4)

            number_columns_verify = []
            for i in dados4.columns:
                for x in columns:
                    if i in x:
                        number_columns_verify.append(x)

            if(dados4.shape[1] == len(columns)) & (len(number_columns_verify) == dados4.shape[1]):

                # if dados4.shape[1] != number_len:
                #     st.write("Tipo errado")
                # st.write(dados4.shape[1])
                # st.write(number_len)

                st.dataframe(dados4)
                name = st.text_input("Nome da unidade")
                date = st.text_input("Data do envio da tabela")
                nameFinal = name+date+str(selection_type)

                ssl_args = {'ssl': "cacert-2023-01-10.pem"}

                engine = create_engine(
                    'mysql+mysqldb://'+st.secrets["db_username"]+':'+st.secrets["db_password"]+'@aws.connect.psdb.cloud/database', connect_args=ssl_args)
                # engine = create_engine(
                #     'mysql+mysqldb://root:02041224dD@127.0.0.1/sex')
                send_table = st.button("Enviar Tabela")
                if send_table:
                    dados4.to_sql(nameFinal, con=engine,
                                  if_exists='replace', index=False)
            else:
                st.error("Tipo não compatível")
elif authentication_status == False:
    st.error('Senha ou Usuario esta incorreto')
elif authentication_status == None:
    st.warning('Insira senha e usuario como solicitado')

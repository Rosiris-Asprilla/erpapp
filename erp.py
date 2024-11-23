#%%writefile erp_streamlit.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from fpdf import FPDF

logo_path = "https://efectonegocio.com/wp-content/uploads/2018/11/ERP.jpg"
# Configuración inicial
st.set_page_config(page_title="Módulos del ERP", layout="wide",page_icon=logo_path)
# Ruta del archivo de imagen (logo)

# Mostrar el logo en la parte superior de la aplicación
st.image(logo_path, width=200)  # Puedes ajustar el tamaño cambiando el valor de 'width'

# Agregar un título o contenido a la aplicación
st.title("Sistema ERP")
st.write("Bienvenido al sistema ERP para la gestión de clientes, inventarios, facturación, reportes y análisis de ventas.")

st.sidebar.title("ERP_ITM")

# Variables de autenticación
USER = "Lira"
PASSWORD = "Lir@1120"

# Inicialización de variables globales
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if "modulo_seleccionado" not in st.session_state:
    st.session_state["modulo_seleccionado"] = None

# Parámetros de ID
if "id_cliente" not in st.session_state:
    st.session_state["id_cliente"] = 1  # El primer ID de cliente

if "id_producto" not in st.session_state:
    st.session_state["id_producto"] = 1  # El primer ID de producto

if "id_factura" not in st.session_state:
    st.session_state["id_factura"] = 1  # El primer ID de factura

# Inicialización de DataFrames
if "clientes" not in st.session_state:
    st.session_state["clientes"] = pd.DataFrame(columns=["ID", "Nombre", "Correo", "Teléfono"])

if "productos" not in st.session_state:
    st.session_state["productos"] = pd.DataFrame(columns=["ID", "Producto", "Cantidad", "Precio Unitario"])

if "facturas" not in st.session_state:
    st.session_state["facturas"] = pd.DataFrame(columns=["Factura ID", "Cliente ID", "Cliente Nombre", "Productos", "Total", "IVA", "Fecha"])
    
# Función de autenticación
with st.sidebar:
    st.title("Módulos ERP")
if not st.session_state["auth"]:
    st.sidebar.subheader("Iniciar Sesión")
    usuario = st.sidebar.text_input("Usuario")
    contraseña = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if usuario == USER and contraseña == PASSWORD:
            st.session_state["auth"] = True
            st.sidebar.success("Inicio de sesión exitoso.")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos.")
else:
    st.sidebar.subheader(f"Bienvenido, {USER}")
    st.session_state["modulo_seleccionado"] = st.sidebar.radio(
        "Selecciona un módulo:",
        ["Gestión de Clientes", "Gestión de Inventario", "Generar Factura", "Generar Reportes", "Análisis de Ventas"],
    )
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["auth"] = False
        st.session_state["modulo_seleccionado"] = None
        st.sidebar.success("Sesión cerrada correctamente.")


# Funciones auxiliares
def exportar_csv(df, nombre_archivo):
    """Permite exportar un DataFrame como archivo CSV."""
    st.download_button(
        label="Exportar Datos",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=nombre_archivo,
        mime="text/csv",
    )

# Funciones de los módulos
def gestion_clientes():
    st.header("Gestión de Clientes")
    
    # Registro de nuevo cliente
    with st.form("Registro de Cliente"):
        nombre = st.text_input("Nombre")
        correo = st.text_input("Correo Electrónico")
        telefono = st.text_input("Teléfono")
        submitted = st.form_submit_button("Registrar Cliente")
        
        if submitted:
            # Generación de ID para el nuevo cliente
            cliente_id = st.session_state["id_cliente"]
            nuevo_cliente = pd.DataFrame([{
                "ID": cliente_id, "Nombre": nombre, "Correo": correo, "Teléfono": telefono
            }])
            st.session_state["clientes"] = pd.concat([st.session_state["clientes"], nuevo_cliente], ignore_index=True)
            st.session_state["id_cliente"] += 1  # Incrementar el ID para el siguiente cliente
            st.success(f"Cliente {nombre} registrado correctamente con ID: {cliente_id}.")
    
    # Búsqueda de clientes
    st.subheader("Buscar Cliente")
    search_term = st.text_input("Buscar por nombre o ID")
    if search_term:
        clientes_filtrados = st.session_state["clientes"][st.session_state["clientes"]["Nombre"].str.contains(search_term, case=False)]
        st.dataframe(clientes_filtrados)
    else:
        st.dataframe(st.session_state["clientes"])

    # Edición de cliente
    cliente_a_editar = st.selectbox("Seleccionar cliente para editar", st.session_state["clientes"]["ID"])
    cliente_data = st.session_state["clientes"][st.session_state["clientes"]["ID"] == cliente_a_editar]
    if cliente_data.empty:
        st.warning("Cliente no encontrado.")
    else:
        with st.form("Editar Cliente"):
            nombre_edit = st.text_input("Nuevo Nombre", cliente_data["Nombre"].values[0])
            correo_edit = st.text_input("Nuevo Correo", cliente_data["Correo"].values[0])
            telefono_edit = st.text_input("Nuevo Teléfono", cliente_data["Teléfono"].values[0])
            submitted_edit = st.form_submit_button("Actualizar Cliente")
            
            if submitted_edit:
                st.session_state["clientes"].loc[st.session_state["clientes"]["ID"] == cliente_a_editar, "Nombre"] = nombre_edit
                st.session_state["clientes"].loc[st.session_state["clientes"]["ID"] == cliente_a_editar, "Correo"] = correo_edit
                st.session_state["clientes"].loc[st.session_state["clientes"]["ID"] == cliente_a_editar, "Teléfono"] = telefono_edit
                st.success(f"Cliente con ID {cliente_a_editar} actualizado.")

    # Eliminación de cliente
    cliente_a_eliminar = st.selectbox("Seleccionar cliente para eliminar", st.session_state["clientes"]["ID"])
    if st.button("Eliminar Cliente"):
        st.session_state["clientes"] = st.session_state["clientes"][st.session_state["clientes"]["ID"] != cliente_a_eliminar]
        st.success("Cliente eliminado correctamente.")

def gestion_inventario():

    st.header("Gestión de Inventario")
    
    # Registro de producto
    with st.form("Registro de Producto"):
        producto = st.text_input("Producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input("Precio Unitario", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Registrar Producto")
        
        if submitted:
            # Generación de ID para el nuevo producto
            producto_id = st.session_state["id_producto"]
            nuevo_producto = pd.DataFrame([{
                "ID": producto_id, "Producto": producto, "Cantidad": cantidad, "Precio Unitario": precio_unitario
            }])
            st.session_state["productos"] = pd.concat([st.session_state["productos"], nuevo_producto], ignore_index=True)
            st.session_state["id_producto"] += 1  # Incrementar el ID para el siguiente producto
            st.success(f"Producto {producto} registrado correctamente con ID: {producto_id}.")
    
    # Búsqueda de productos
    st.subheader("Buscar Producto")
    search_term = st.text_input("Buscar producto por nombre")
    if search_term:
        inventario_filtrado = st.session_state["productos"][st.session_state["productos"]["Producto"].str.contains(search_term, case=False)]
        st.dataframe(inventario_filtrado)
    else:
        st.dataframe(st.session_state["productos"])

    # Eliminación de producto
    producto_a_eliminar = st.selectbox("Seleccionar producto para eliminar", st.session_state["productos"]["Producto"])
    if st.button("Eliminar Producto"):
        st.session_state["productos"] = st.session_state["productos"][st.session_state["productos"]["Producto"] != producto_a_eliminar]
        st.success("Producto eliminado correctamente.")

def gestion_facturas():
    st.header("Generar Factura")
    st.write("Selecciona un cliente y productos para crear una factura.")
    
    if st.session_state["clientes"].empty:
        st.warning("No hay clientes registrados. Por favor, registra clientes antes de crear una factura.")
        return
    
    if st.session_state["productos"].empty:
        st.warning("No hay productos en el inventario. Por favor, registra productos antes de crear una factura.")
        return
    
    cliente_id = st.selectbox("Seleccionar Cliente", st.session_state["clientes"]["ID"])
    cliente_nombre = st.session_state["clientes"].loc[
        st.session_state["clientes"]["ID"] == cliente_id, "Nombre"
    ].values[0]
    
    # Selección de productos
    productos_seleccionados = st.multiselect(
        "Selecciona productos", 
        st.session_state["productos"]["Producto"].values
    )
    
    if not productos_seleccionados:
        st.info("Selecciona al menos un producto para generar una factura.")
        return
    
    productos_detalle = []
    total = 0
    
    for producto in productos_seleccionados:
        producto_info = st.session_state["productos"].loc[
            st.session_state["productos"]["Producto"] == producto
        ]
        precio_unitario = producto_info["Precio Unitario"].values[0]
        stock_disponible = producto_info["Cantidad"].values[0]
        
        # Selección de cantidad
        cantidad = st.number_input(
            f"Cantidad de {producto} (Disponible: {stock_disponible})", 
            min_value=1, 
            max_value=stock_disponible, 
            step=1
        )
        
        subtotal = precio_unitario * cantidad
        total += subtotal
        productos_detalle.append({
            "Producto": producto,
            "Cantidad": cantidad,
            "Precio Unitario": precio_unitario,
            "Subtotal": subtotal
        })
    
    # Calcular IVA y total final
    iva = total * 0.16
    total_con_iva = total + iva
    
    # Mostrar resumen
    st.subheader("Resumen de Factura")
    st.table(pd.DataFrame(productos_detalle))
    st.write(f"Subtotal: ${total:,.2f}")
    st.write(f"IVA (16%): ${iva:,.2f}")
    st.write(f"Total: ${total_con_iva:,.2f}")
    
    # Confirmación y registro de factura
    if st.button("Confirmar y Generar Factura"):
        factura_id = st.session_state["id_factura"]
        fecha = pd.to_datetime("today").strftime("%Y-%m-%d")
        
        # Registrar factura
        factura = pd.DataFrame([{
            "Factura ID": factura_id, 
            "Cliente ID": cliente_id, 
            "Cliente Nombre": cliente_nombre,
            "Productos": productos_detalle, 
            "Total": total, 
            "IVA": iva, 
            "Fecha": fecha
        }])
        st.session_state["facturas"] = pd.concat([st.session_state["facturas"], factura], ignore_index=True)
        st.session_state["id_factura"] += 1  # Incrementar el ID para la siguiente factura
        
        # Reducir inventario
        for detalle in productos_detalle:
            producto = detalle["Producto"]
            cantidad = detalle["Cantidad"]
            st.session_state["productos"].loc[
                st.session_state["productos"]["Producto"] == producto, "Cantidad"
            ] -= cantidad
        
        st.success(f"Factura {factura_id} generada correctamente.")
        st.write(f"Total con IVA: ${total_con_iva:,.2f}")
        
        # Exportar factura
        exportar_csv(st.session_state["facturas"], f"factura_{factura_id}.csv")

def gestion_reportes():
 

    st.header("Generar Reportes")

    # Generación de reportes contables
    st.write("Aquí pueden ir los reportes contables.")
    st.write("Funciones específicas para reportes como ingresos, gastos y balances se agregarán aquí.")
    
    # Simulando el reporte básico
    st.text_area("Resumen", "Reporte generado: ingresos, gastos, balance general, etc.")
    
    # Exportar el reporte a CSV
    exportar_csv(st.session_state["facturas"], "reportes_contables.csv")

import plotly.express as px

def analisis_ventas():
    st.header("Análisis de Ventas")
    
    # Verificar si hay datos en las facturas
    if st.session_state["facturas"].empty:
        st.warning("No hay datos de facturas para analizar.")
        return

    # Crear una lista para desglosar productos en facturas
    productos_desglosados = []
    for _, fila in st.session_state["facturas"].iterrows():
        for producto in fila["Productos"]:
            productos_desglosados.append({
                "Producto": producto["Producto"],
                "Cantidad": producto["Cantidad"],
                "Subtotal": producto["Subtotal"],
                "Fecha": fila["Fecha"]
            })

    # Crear un DataFrame con los datos desglosados
    df_productos = pd.DataFrame(productos_desglosados)

    # Verificar si hay datos en el DataFrame desglosado
    if df_productos.empty:
        st.warning("No hay datos suficientes para generar análisis.")
        return

    # Análisis de ventas por producto
    st.subheader("Ventas por Producto")
    ventas_por_producto = df_productos.groupby("Producto").sum().reset_index()
    fig1 = px.bar(
        ventas_por_producto, 
        x="Producto", 
        y="Subtotal", 
        title="Ingresos por Producto", 
        labels={"Subtotal": "Ingresos ($)"},
        text="Subtotal"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Análisis de cantidades vendidas por producto
    st.subheader("Cantidad Vendida por Producto")
    fig2 = px.pie(
        ventas_por_producto, 
        names="Producto", 
        values="Cantidad", 
        title="Distribución de Cantidades Vendidas"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Análisis temporal de ventas
    st.subheader("Ingresos Totales por Fecha")
    df_productos["Fecha"] = pd.to_datetime(df_productos["Fecha"])
    ingresos_por_fecha = df_productos.groupby("Fecha").sum().reset_index()
    fig3 = px.line(
        ingresos_por_fecha, 
        x="Fecha", 
        y="Subtotal", 
        title="Evolución de Ingresos en el Tiempo",
        labels={"Subtotal": "Ingresos ($)", "Fecha": "Fecha"}
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.success("Gráficos interactivos generados correctamente.")

# Navegación entre módulos
if st.session_state["auth"]:
    if st.session_state["modulo_seleccionado"] == "Gestión de Clientes":
        gestion_clientes()
    elif st.session_state["modulo_seleccionado"] == "Gestión de Inventario":
        gestion_inventario()
    elif st.session_state["modulo_seleccionado"] == "Generar Factura":
        gestion_facturas()
    elif st.session_state["modulo_seleccionado"] == "Generar Reportes":
        gestion_reportes()
    elif st.session_state["modulo_seleccionado"] == "Análisis de Ventas":
        analisis_ventas()
else:
    st.warning("Por favor, inicia sesión para continuar.")

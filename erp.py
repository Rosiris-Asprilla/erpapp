import streamlit as st
import pandas as pd
from fpdf import FPDF

# Configuración inicial
st.set_page_config(page_title="ERP con Autenticación", layout="wide")

# Variables de autenticación
USER = "Lira"
PASSWORD = "Lir@1120"

# Inicialización de variables globales
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if "modulo" not in st.session_state:
    st.session_state["modulo"] = "Gestión de Clientes"

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
def autenticar_usuario():
    if not st.session_state["auth"]:
        with st.form(key="login_form"):
            usuario = st.text_input("Usuario")
            contraseña = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")
            
            if submitted:
                if usuario == USER and contraseña == PASSWORD:
                    st.session_state["auth"] = True
                    st.success("Autenticación exitosa")
                else:
                    st.error("Usuario o contraseña incorrectos")
        return False
    return True

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
    if not autenticar_usuario():
        return  # Si no está autenticado, no se permite acceder a los módulos

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

    # Eliminación de cliente
    cliente_a_eliminar = st.selectbox("Seleccionar cliente para eliminar", st.session_state["clientes"]["ID"])
    if st.button("Eliminar Cliente"):
        st.session_state["clientes"] = st.session_state["clientes"][st.session_state["clientes"]["ID"] != cliente_a_eliminar]
        st.success("Cliente eliminado correctamente.")

def gestion_inventario():
    if not autenticar_usuario():
        return  # Si no está autenticado, no se permite acceder a los módulos

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
    if not autenticar_usuario():
        return  # Si no está autenticado, no se permite acceder a los módulos

    st.header("Generar Factura")
    st.write("Selecciona un cliente y productos para crear una factura.")

    cliente_id = st.selectbox("Seleccionar Cliente", st.session_state["clientes"]["ID"])
    cliente_nombre = st.session_state["clientes"][st.session_state["clientes"]["ID"] == cliente_id]["Nombre"].values[0]
    
    productos_seleccionados = []
    total = 0
    iva = 0
    
    for producto in st.session_state["productos"]["Producto"]:
        cantidad = st.number_input(f"Cantidad de {producto}", min_value=0, step=1)
        if cantidad > 0:
            producto_data = st.session_state["productos"][st.session_state["productos"]["Producto"] == producto]
            precio_unitario = producto_data["Precio Unitario"].values[0]
            total += cantidad * precio_unitario
            productos_seleccionados.append((producto, cantidad, precio_unitario))
    
    iva = total * 0.16
    total_con_iva = total + iva
    
    if st.button("Generar Factura"):
        # Generación de ID para la nueva factura
        factura_id = st.session_state["id_factura"]
        st.session_state["facturas"] = st.session_state["facturas"].append({
            "Factura ID": factura_id,
            "Cliente ID": cliente_id,
            "Cliente Nombre": cliente_nombre,
            "Productos": productos_seleccionados,
            "Total": total_con_iva,
            "IVA": iva,
            "Fecha": pd.Timestamp.now().strftime('%Y-%m-%d')
        }, ignore_index=True)
        st.session_state["id_factura"] += 1  # Incrementar el ID para la siguiente factura
        st.success(f"Factura {factura_id} generada correctamente.")
    
    st.dataframe(st.session_state["facturas"])
    exportar_csv(st.session_state["facturas"], "facturas.csv")

def analisis_ventas():
    if not autenticar_usuario():
        return  # Si no está autenticado, no se permite acceder a los módulos

    st.header("Análisis de Ventas")
    if st.session_state["facturas"].empty:
        st.warning("No hay ventas registradas.")
    else:
        st.subheader("Ventas Realizadas")
        st.dataframe(st.session_state["facturas"])
        
        # Total de ventas
        total_ventas = st.session_state["facturas"]["Total"].sum()
        st.write(f"**Total de Ventas: ${total_ventas:,.2f}**")
        
        # Reporte de ventas por cliente
        ventas_por_cliente = st.session_state["facturas"].groupby("Cliente Nombre")["Total"].sum()
        st.write("**Ventas por Cliente:**")
        st.dataframe(ventas_por_cliente)

def gestion_reportes():
    if not autenticar_usuario():
        return  # Si no está autenticado, no se permite acceder a los módulos

    st.header("Generación de Reportes Contables")
    if st.button("Generar Reporte Contable"):
        # Generación de un reporte simple en PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Reporte Contable", ln=True, align="C")
        pdf.ln(10)
        
        # Exportar el reporte
        st.download_button(
            label="Descargar Reporte Contable",
            data=pdf.output(dest="S").encode("latin1"),
            file_name="reporte_contable.pdf",
            mime="application/pdf"
        )

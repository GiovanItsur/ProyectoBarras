from BackEnd.conexion import Conexion


class PuntoDeVentaBackend:

    def buscar_producto(self, codigo_ingresado):
        #En lo único que se fija es en el código que ingresé en la BD y
        #el lector solo lo escribe rápidamente para iniciar la busqueda
        objeto_conexion = Conexion()
        conexion = objeto_conexion.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                # AHORA PEDIMOS EL id_producto TAMBIÉN
                sql = "SELECT id_producto, descripcion, precio, stock FROM productos WHERE codigo_barras = %s"
                cursor.execute(sql, (codigo_ingresado,))
                producto = cursor.fetchone()

                if producto:
                    return True, producto
                else:
                    return False, "Producto no encontrado."
            except Exception as e:
                return False, f"Error en BD: {e}"
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False, "Error de conexión."

    def guardar_venta(self, empleado, subtotal, iva, total, carrito):

        objeto_conexion = Conexion()
        conexion = objeto_conexion.conectar()

        if conexion:
            try:
                conexion.autocommit = False
                cursor = conexion.cursor()

                sql_venta = """
                    INSERT INTO ventas (empleado, subtotal, iva, total) 
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(sql_venta, (empleado, subtotal, iva, total))
                folio_generado = cursor.lastrowid

                sql_detalle = """
                    INSERT INTO detalles_venta (folio_venta, id_producto, cantidad, precio, importe) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                sql_stock = """
                    UPDATE productos 
                    SET stock = stock - %s 
                    WHERE id_producto = %s
                """

                for item in carrito:
                    id_prod = item[0]
                    cantidad = item[1]
                    precio = item[2]
                    importe = item[3]

                    cursor.execute(sql_detalle, (folio_generado, id_prod, cantidad, precio, importe))
                    cursor.execute(sql_stock, (cantidad, id_prod))

                conexion.commit()
                return True, f"Venta {folio_generado} registrada con éxito."

            except Exception as e:
                conexion.rollback()
                return False, f"Transacción cancelada: {e}"
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False, "Error de conexión."
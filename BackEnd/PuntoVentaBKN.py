from BackEnd.conexion import Conexion


class PuntoDeVentaBackend:

    def buscar_producto(self, clave_producto):
        #En lo único que se fija es en el código que ingresé en la BD y
        #el lector solo lo escribe rápidamente para iniciar la busqueda
        objeto_conexion = Conexion()
        conexion = objeto_conexion.conectar()

        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "SELECT descripcion, precio, stock FROM productos WHERE clave = %s"
                #Se busca el producto directamente por solo la clave
                cursor.execute(sql, (clave_producto,))
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
                            VALUES (%s, %s, %s, %s) \
                            """
                cursor.execute(sql_venta, (empleado, subtotal, iva, total))

                folio_generado = cursor.lastrowid

                sql_detalle = """
                              INSERT INTO detalles_venta (folio_venta, clave_producto, cantidad, precio, importe)
                              VALUES (%s, %s, %s, %s, %s) \
                              """
                sql_stock = """
                            UPDATE productos
                            SET stock = stock - %s
                            WHERE clave = %s \
                            """
                for item in carrito:
                    clave = item[0]
                    cantidad = item[1]
                    precio = item[2]
                    importe = item[3]
                    cursor.execute(sql_detalle, (folio_generado, clave, cantidad, precio, importe))

                    cursor.execute(sql_stock, (cantidad, clave))
                conexion.commit()
                return True, f"Venta {folio_generado} registrada con éxito."

            except Exception as e:
                conexion.rollback()
                return False, f"Error al procesar la venta. Transacción cancelada: {e}"
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
        return False, "Error de conexión."
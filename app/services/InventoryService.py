from mysql.connector import Error
from app.models.entities import InventoryItem, StockMovement
from app.exceptions import ValidationError, NotFoundError, DatabaseError
import logging


logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, db):
        self.db = db

    def fetch_all(self):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT ii.id, ii.part_name, ii.category, ii.brand, ii.model_number, 
                       ii.quantity, ii.cost_price, ii.selling_price, ii.supplier_id,
                       COALESCE(s.name, 'N/A') as supplier_name
                FROM inventory_items ii
                LEFT JOIN suppliers s ON ii.supplier_id = s.id
                ORDER BY ii.part_name
            """)
            results = cursor.fetchall()
            return [self._map_row_to_item(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to fetch inventory: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def create_item(self, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id, performed_by=None):
        if not part_name or not part_name.strip():
            raise ValidationError("Part name is required")
        
        try:
            quantity = int(quantity)
            cost_price = float(cost_price)
            selling_price = float(selling_price)
        except (ValueError, TypeError):
            raise ValidationError("Invalid quantity or price values")
        
        if cost_price < 0 or selling_price < 0:
            raise ValidationError("Prices cannot be negative")
        
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        
        if selling_price < cost_price:
            raise ValidationError("Selling price cannot be below cost price")
        
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO inventory_items 
                (part_name, category, brand, model_number, quantity, 
                 cost_price, selling_price, supplier_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id))
            self.db.commit()
            item_id = cursor.lastrowid
            # Log with INVENTORY_UPDATED event type
            inv_logger = logging.getLogger('INVENTORY_UPDATED')
            if performed_by:
                inv_logger.info(f"Inventory item created: {part_name} (ID: {item_id}) - Username: {performed_by}")
            else:
                inv_logger.info(f"Inventory item created: {part_name} (ID: {item_id})")
            return self.get_by_id(item_id)
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to create inventory item: {str(e)}")
            raise DatabaseError(f"Failed to create item: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def update_item(self, item_id, part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id, performed_by=None):
        if not part_name or not part_name.strip():
            raise ValidationError("Part name is required")
        
        try:
            quantity = int(quantity)
            cost_price = float(cost_price)
            selling_price = float(selling_price)
        except (ValueError, TypeError):
            raise ValidationError("Invalid quantity or price values")
        
        if cost_price < 0 or selling_price < 0:
            raise ValidationError("Prices cannot be negative")
        
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative")
        
        if selling_price < cost_price:
            raise ValidationError("Selling price cannot be below cost price")
        
        existing = self.get_by_id(item_id)
        if not existing:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                UPDATE inventory_items SET 
                    part_name=%s, category=%s, brand=%s, model_number=%s,
                    quantity=%s, cost_price=%s, selling_price=%s, supplier_id=%s
                WHERE id=%s
            """, (part_name, category, brand, model_number, quantity, cost_price, selling_price, supplier_id, item_id))
            self.db.commit()
            inv_logger = logging.getLogger('INVENTORY_UPDATED')
            if performed_by:
                inv_logger.info(f"Inventory item updated: {part_name} (ID: {item_id}) - Username: {performed_by}")
            else:
                inv_logger.info(f"Inventory item updated: {part_name} (ID: {item_id})")
            return self.get_by_id(item_id)
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to update inventory item: {str(e)}")
            raise DatabaseError(f"Failed to update item: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def delete_item(self, item_id, performed_by=None):
        existing = self.get_by_id(item_id)
        if not existing:
            raise NotFoundError(f"Item with ID {item_id} not found")
        
        cursor = None
        try:
            item_name = existing.part_name
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM inventory_items WHERE id=%s", (item_id,))
            self.db.commit()
            # Log with INVENTORY_UPDATED event type
            inv_logger = logging.getLogger('INVENTORY_UPDATED')
            if performed_by:
                inv_logger.info(f"Inventory item deleted: {item_name} (ID: {item_id}) - Username: {performed_by}")
            else:
                inv_logger.info(f"Inventory item deleted: {item_name} (ID: {item_id})")
            return True
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to delete inventory item: {str(e)}")
            raise DatabaseError(f"Failed to delete item: {str(e)}")
        finally:
            if cursor:
                cursor.close()









    def get_by_id(self, item_id):
        cursor = None
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT ii.id, ii.part_name, ii.category, ii.brand, ii.model_number, 
                       ii.quantity, ii.cost_price, ii.selling_price, ii.supplier_id,
                       COALESCE(s.name, 'N/A') as supplier_name
                FROM inventory_items ii
                LEFT JOIN suppliers s ON ii.supplier_id = s.id
                WHERE ii.id=%s
            """, (item_id,))
            result = cursor.fetchone()
            return self._map_row_to_item(result) if result else None
        except Error as e:
            raise DatabaseError(f"Failed to get item: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def record_stock_movement(self, item_id, movement_type, quantity, reason, notes, user_id=None):
        if movement_type not in ("IN", "OUT", "ADJUSTMENT"):
            raise ValidationError("Invalid movement type")
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            raise ValidationError("Invalid quantity")
        
        if quantity <= 0 and movement_type != "ADJUSTMENT":
            raise ValidationError("Quantity must be positive")

        cursor = None
        try:
            cursor = self.db.cursor()

            cursor.execute("SELECT quantity FROM inventory_items WHERE id=%s", (item_id,))
            result = cursor.fetchone()
            if not result:
                raise NotFoundError(f"Item with ID {item_id} not found")

            current_qty = result[0]

            if movement_type == "IN":
                new_qty = current_qty + quantity
            elif movement_type == "OUT":
                new_qty = current_qty - quantity
                if new_qty < 0:
                    raise ValidationError(f"Insufficient stock. Available: {current_qty}, Requested: {quantity}")
            else:
                new_qty = quantity

            cursor.execute("""
                INSERT INTO stock_movements 
                (item_id, movement_type, quantity, reason, notes, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (item_id, movement_type, quantity, reason, notes, user_id))

            movement_id = cursor.lastrowid

            cursor.execute(
                "UPDATE inventory_items SET quantity=%s WHERE id=%s",
                (new_qty, item_id)
            )

            self.db.commit()
            # Log with INVENTORY_UPDATED event type
            inv_logger = logging.getLogger('INVENTORY_UPDATED')
            inv_logger.info(f"Stock movement recorded: Type={movement_type}, Item ID={item_id}, Quantity={quantity}, Reason={reason}")
            return movement_id
        except (ValidationError, NotFoundError):
            raise
        except Error as e:
            self.db.rollback()
            logger.error(f"Failed to record stock movement: {str(e)}")
            raise DatabaseError(f"Failed to record stock movement: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def get_stock_movements(self, item_id=None, limit=100):
        cursor = None
        try:
            cursor = self.db.cursor()
            if item_id:
                cursor.execute("""
                    SELECT sm.id, sm.item_id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    WHERE sm.item_id = %s
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """, (item_id, limit))
            else:
                cursor.execute("""
                    SELECT sm.id, sm.item_id, ii.part_name, sm.movement_type, sm.quantity, sm.reason, 
                           sm.notes, sm.movement_date, COALESCE(u.full_name, u.username, 'System')
                    FROM stock_movements sm
                    JOIN inventory_items ii ON sm.item_id = ii.id
                    LEFT JOIN users u ON sm.created_by = u.id
                    ORDER BY sm.movement_date DESC
                    LIMIT %s
                """, (limit,))
            results = cursor.fetchall()
            return [self._map_row_to_movement(row) for row in results]
        except Error as e:
            raise DatabaseError(f"Failed to get stock movements: {str(e)}")
        finally:
            if cursor:
                cursor.close()

    def _map_row_to_item(self, row):
        if not row:
            return None
        return InventoryItem(
            id=row[0],
            part_name=row[1],
            category=row[2],
            brand=row[3],
            model_number=row[4],
            quantity=row[5],
            cost_price=row[6],
            selling_price=row[7],
            supplier_id=row[8],
            supplier_name=row[9] if len(row) > 9 else ""
        )

    def _map_row_to_movement(self, row):
        if not row:
            return None
        return StockMovement(
            id=row[0],
            item_id=row[1],
            item_name=row[2],
            movement_type=row[3],
            quantity=row[4],
            reason=row[5],
            notes=row[6],
            movement_date=row[7],
            username=row[8]
        )

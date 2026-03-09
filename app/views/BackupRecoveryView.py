"""
Backup and Recovery View
Allows users to manage database backups and restore from backups.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QLabel, QMessageBox, QFileDialog, QHeaderView,
    QFrame, QProgressBar, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from pathlib import Path
from app.views.BaseView import BaseView
from app.utils.BackupManager import BackupManager


class BackupRecoveryView(BaseView):
    """Backup and recovery management view"""
    
    def __init__(self, db_connection):
        """
        Initialize Backup Recovery View.
        
        Args:
            db_connection: Database connection object
        """
        super().__init__()
        self.db_connection = db_connection
        self.refresh_in_progress = False
        
        self._setup_ui()
        self.load_backups()
    
    def _setup_ui(self) -> None:
        """Setup user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Database Backup & Recovery")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Control buttons
        button_layout = self._create_button_panel()
        layout.addLayout(button_layout)
        
        # Backups table
        self.backups_table = self._create_backups_table()
        layout.addWidget(self.backups_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #6B7280; font-size: 11px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def _create_button_panel(self) -> QHBoxLayout:
        """Create control buttons"""
        layout = QHBoxLayout()
        
        # Create backup button
        create_btn = QPushButton("Create New Backup")
        create_btn.clicked.connect(self.create_backup)
        layout.addWidget(create_btn)
        
        # Restore button
        restore_btn = QPushButton("Restore Selected")
        restore_btn.clicked.connect(self.restore_backup)
        layout.addWidget(restore_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_backup)
        layout.addWidget(delete_btn)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.load_backups)
        layout.addWidget(refresh_btn)
        
        layout.addStretch()
        
        return layout
    
    def _create_backups_table(self) -> QTableWidget:
        """Create backups table widget"""
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            "Backup File",
            "Size (MB)",
            "Created",
            "Status"
        ])
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setAlternatingRowColors(True)
        
        return table
    
    def load_backups(self) -> None:
        """Load and display backup files"""
        try:
            backups = BackupManager.list_backups()
            self._populate_table(backups)
            self.status_label.setText(f"Found {len(backups)} backup(s)")
        except Exception as e:
            self.status_label.setText(f"Error loading backups: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load backups:\n{str(e)}")
    
    def _populate_table(self, backups: list) -> None:
        """Populate table with backup data"""
        self.backups_table.setRowCount(0)
        
        for row_idx, backup in enumerate(backups):
            self.backups_table.insertRow(row_idx)
            
            # Filename
            filename = backup['name']
            self.backups_table.setItem(row_idx, 0, QTableWidgetItem(filename))
            
            # Size
            size_item = QTableWidgetItem(f"{backup['size_mb']:.2f}")
            size_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.backups_table.setItem(row_idx, 1, size_item)
            
            # Timestamp
            timestamp_str = backup['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            time_item = QTableWidgetItem(timestamp_str)
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.backups_table.setItem(row_idx, 2, time_item)
            
            # Status (✓ for valid)
            status_item = QTableWidgetItem("✓ Valid")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.backups_table.setItem(row_idx, 3, status_item)
            
            # Store path in table item for reference
            filename_item = self.backups_table.item(row_idx, 0)
            filename_item.backup_path = backup['path']
    
    def create_backup(self) -> None:
        """Create a new database backup"""
        try:
            self.status_label.setText("Creating backup...")
            self.setEnabled(False)
            
            # Create backup in background thread
            self.backup_thread = BackupThread(self.db_connection)
            self.backup_thread.finished.connect(self._on_backup_finished)
            self.backup_thread.error.connect(self._on_backup_error)
            self.backup_thread.start()
            
        except Exception as e:
            self.setEnabled(True)
            self.status_label.setText("Error creating backup")
            QMessageBox.critical(self, "Backup Failed", f"Failed to create backup:\n{str(e)}")
    
    def _on_backup_finished(self, result: dict) -> None:
        """Handle backup completion"""
        self.setEnabled(True)
        
        if result['success']:
            size_mb = result['backup_size'] / (1024 * 1024)
            self.status_label.setText(f"Backup created successfully ({size_mb:.2f} MB)")
            QMessageBox.information(
                self,
                "Backup Successful",
                f"Database backed up successfully!\n\n"
                f"File: {result['backup_path']}\n"
                f"Size: {size_mb:.2f} MB"
            )
            self.load_backups()
        else:
            self.status_label.setText("Backup failed")
            QMessageBox.warning(self, "Backup Failed", f"Backup failed:\n{result['message']}")
    
    def _on_backup_error(self, error_msg: str) -> None:
        """Handle backup error"""
        self.setEnabled(True)
        self.status_label.setText("Backup error")
        QMessageBox.critical(self, "Backup Error", f"Backup error:\n{error_msg}")
    
    def restore_backup(self) -> None:
        """Restore database from selected backup"""
        try:
            row = self.backups_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a backup to restore")
                return
            
            filename_item = self.backups_table.item(row, 0)
            backup_path = filename_item.backup_path
            filename = filename_item.text()
            size_mb = float(self.backups_table.item(row, 1).text())
            
            # Confirm restore
            reply = QMessageBox.warning(
                self,
                "Confirm Restore",
                f"Are you sure you want to restore from:\n\n{filename}\n\n"
                f"This will overwrite all current database data!\n\n"
                f"This may take several minutes for large backups ({size_mb:.2f} MB).",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Calculate better time estimate
            # Typical restore speed: 1-2 MB/min depending on system
            min_time = max(1, int(size_mb / 2))  # At least 1 min, or half the size in minutes
            max_time = max(2, int(size_mb))     # At least 2 min, or equal to size in minutes
            
            self.status_label.setText(f"Restoring database... (this may take {min_time}-{max_time} minutes)")
            self.setEnabled(False)
            
            # Restore in background thread
            self.restore_thread = RestoreThread(backup_path, self.db_connection)
            self.restore_thread.finished.connect(self._on_restore_finished)
            self.restore_thread.error.connect(self._on_restore_error)
            self.restore_thread.start()
            
        except Exception as e:
            self.setEnabled(True)
            self.status_label.setText("Error restoring backup")
            QMessageBox.critical(self, "Restore Failed", f"Failed to restore backup:\n{str(e)}")
    
    def _on_restore_finished(self, result: dict) -> None:
        """Handle restore completion"""
        self.setEnabled(True)
        
        if result['success']:
            self.status_label.setText("Database restored successfully")
            QMessageBox.information(
                self,
                "Restore Successful",
                "Database has been restored successfully!\n\n"
                "You may need to restart the application for changes to take effect."
            )
            self.load_backups()
        else:
            self.status_label.setText("Restore failed")
            error_msg = result['message']
            if 'timeout' in error_msg.lower():
                QMessageBox.warning(
                    self, 
                    "Restore Timeout", 
                    f"Restore operation is taking a very long time.\n\n{error_msg}\n\n"
                    f"The database may still be processing. Please wait and check back later."
                )
            else:
                QMessageBox.warning(self, "Restore Failed", f"Restore failed:\n{error_msg}")
    
    def _on_restore_error(self, error_msg: str) -> None:
        """Handle restore error"""
        self.setEnabled(True)
        self.status_label.setText("Restore error")
        QMessageBox.critical(
            self, 
            "Restore Error", 
            f"Restore error:\n{error_msg}\n\n"
            f"Check that MySQL/MariaDB is running and credentials are correct."
        )
    
    def delete_backup(self) -> None:
        """Delete selected backup file"""
        try:
            row = self.backups_table.currentRow()
            if row < 0:
                QMessageBox.warning(self, "No Selection", "Please select a backup to delete")
                return
            
            filename_item = self.backups_table.item(row, 0)
            backup_path = filename_item.backup_path
            filename = filename_item.text()
            
            # Confirm delete
            reply = QMessageBox.warning(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete:\n\n{filename}\n\n"
                f"This cannot be undone!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            result = BackupManager.delete_backup(backup_path)
            
            if result['success']:
                self.status_label.setText("Backup deleted")
                self.load_backups()
                QMessageBox.information(self, "Success", result['message'])
            else:
                self.status_label.setText("Delete failed")
                QMessageBox.warning(self, "Delete Failed", result['message'])
                
        except Exception as e:
            self.status_label.setText("Error deleting backup")
            QMessageBox.critical(self, "Error", f"Failed to delete backup:\n{str(e)}")


class BackupThread(QThread):
    """Background thread for database backup"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
    
    def run(self):
        try:
            result = BackupManager.create_backup(db_connection=self.db_connection)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class RestoreThread(QThread):
    """Background thread for database restore"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, backup_file: str, db_connection):
        super().__init__()
        self.backup_file = backup_file
        self.db_connection = db_connection
    
    def run(self):
        try:
            result = BackupManager.restore_backup(self.backup_file, self.db_connection)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

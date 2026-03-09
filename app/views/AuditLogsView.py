"""
Audit Logs View - Real-Time Log Monitoring
Displays security events and system logs with filtering, searching, and export capabilities.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
    QTableWidgetItem, QComboBox, QLineEdit, QLabel, QSpinBox, 
    QCheckBox, QHeaderView, QFileDialog, QMessageBox, QDateTimeEdit
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal
from PyQt6.QtGui import QColor, QFont
import csv
from datetime import datetime, timedelta
from app.views.BaseView import BaseView
from typing import Optional, List, Dict, Any


class AuditLogsView(BaseView):
    """Real-time audit log viewer with filtering and export"""
    
    # Signal for log refresh
    logs_refreshed = pyqtSignal(list)
    
    def __init__(self, db_connection):
        """
        Initialize Audit Logs View.
        
        Args:
            db_connection: Database connection object
        """
        super().__init__()
        self.db_connection = db_connection
        self.current_logs = []
        self.auto_refresh = True
        self.refresh_interval = 5000  # 5 seconds
        
        # Setup auto-refresh timer BEFORE UI setup
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_logs)
        
        # Setup UI
        self._setup_ui()
        
        # Connect signals
        self.logs_refreshed.connect(self._on_logs_refreshed)
        
        # Load initial logs and start auto-refresh
        self._refresh_logs()
        self.refresh_timer.start(self.refresh_interval)
    
    def _setup_ui(self) -> None:
        """Setup user interface"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Security Audit Logs")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
       
        
        # Filter panel
        filter_layout = self._create_filter_panel()
        layout.addLayout(filter_layout)
        
        # Logs table
        self.logs_table = self._create_logs_table()
        layout.addWidget(self.logs_table)
        
        # Action buttons
        button_layout = self._create_button_panel()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _create_filter_panel(self) -> QHBoxLayout:
        """Create filter controls"""
        layout = QHBoxLayout()
        
        # Event type filter
        layout.addWidget(QLabel("Event Type:"))
        self.event_filter = QComboBox()
        self.event_filter.addItems([
            "ALL", "AUTH", "PASSWORD_CHANGE", "USER_CREATED", 
            "USER_DELETED", "INVENTORY_UPDATED", 
            "CAPTCHA_FAILED", "ACCOUNT_LOCKED"
        ])
        self.event_filter.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.event_filter)
        
        # Log level filter
        layout.addWidget(QLabel("Level:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self._on_filter_changed)
        layout.addWidget(self.level_filter)
        
        # Username filter
        layout.addWidget(QLabel("User:"))
        self.user_filter = QLineEdit()
        self.user_filter.setPlaceholderText("Search username...")
        self.user_filter.setMaximumWidth(150)
        self.user_filter.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.user_filter)
        
        # Time range
        layout.addWidget(QLabel("Last:"))
        self.time_span = QSpinBox()
        self.time_span.setValue(1)
        self.time_span.setMinimum(1)
        self.time_span.setMaximum(24)
        self.time_span.setSuffix(" hours")
        self.time_span.valueChanged.connect(self._on_filter_changed)
        layout.addWidget(self.time_span)
        
        # Search box
        layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search in details...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.search_box)
        
        # Auto-refresh checkbox
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self._toggle_auto_refresh)
        layout.addWidget(self.auto_refresh_check)
        
        layout.addStretch()
        
        return layout
    
    def _create_logs_table(self) -> QTableWidget:
        """Create logs table widget"""
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels([
            "Timestamp",
            "Event Type",
            "Level",
            "Username",
            "Action",
            "Status",
            "Details"
        ])
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Timestamp
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Event Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Level
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Username
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Action
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # Details
        
        # Allow sorting
        table.setSortingEnabled(True)
        table.setAlternatingRowColors(True)
        
        return table
    
    def _create_button_panel(self) -> QHBoxLayout:
        """Create action buttons"""
        layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Now")
        refresh_btn.clicked.connect(self._refresh_logs)
        layout.addWidget(refresh_btn)
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self._clear_filters)
        layout.addWidget(clear_btn)
        
        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self._export_to_csv)
        layout.addWidget(export_btn)
        
        # Statistics button
        stats_btn = QPushButton("Show Statistics")
        stats_btn.clicked.connect(self._show_statistics)
        layout.addWidget(stats_btn)
        
        layout.addStretch()
        
        return layout
    
    def _refresh_logs(self) -> None:
        """Refresh logs from database"""
        try:
            logs = self._fetch_logs()
            self.logs_refreshed.emit(logs)
        except Exception as e:
            print(f"Error refreshing logs: {str(e)}")
    
    def _fetch_logs(self) -> List[Dict[str, Any]]:
        """Fetch logs from database with current filters"""
        if not self.db_connection:
            return []
        
        cursor = None
        try:
            cursor = self.db_connection.cursor(dictionary=True)
            
            # Build query - exclude non-security logs
            sql = """SELECT * FROM security_audit_logs WHERE 1=1 
                     AND event_type NOT IN ('INVENTORYCONTROLLER', 'SUPPLIERSERVICE', 'INVENTORYSERVICE')"""
            params = []
            
            # Event type filter
            event_type = self.event_filter.currentText()
            if event_type != "ALL":
                sql += " AND event_type = %s"
                params.append(event_type)
            
            # Level filter (map to database level value)
            level = self.level_filter.currentText()
            if level != "ALL":
                sql += " AND level = %s"
                params.append(level)
            
            # Time range filter
            time_hours = self.time_span.value()
            time_threshold = datetime.now() - timedelta(hours=time_hours)
            sql += " AND timestamp >= %s"
            params.append(time_threshold)
            
            # Username filter
            username = self.user_filter.text().strip()
            if username:
                sql += " AND username LIKE %s"
                params.append(f"%{username}%")
            
            # Search filter
            search_term = self.search_box.text().strip()
            if search_term:
                sql += " AND details LIKE %s"
                params.append(f"%{search_term}%")
            
            # Order by timestamp descending
            sql += " ORDER BY timestamp DESC LIMIT 1000"
            
            cursor.execute(sql, params)
            logs = cursor.fetchall()
            
            return logs if logs else []
            
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def _on_logs_refreshed(self, logs: List[Dict[str, Any]]) -> None:
        """Update table with fetched logs"""
        self.current_logs = logs
        self._populate_table(logs)
    
    def _populate_table(self, logs: List[Dict[str, Any]]) -> None:
        """Populate table with log data"""
        self.logs_table.setRowCount(0)
        
        for row_idx, log in enumerate(logs):
            self.logs_table.insertRow(row_idx)
            
            # Timestamp
            timestamp = log.get('timestamp', '')
            self.logs_table.setItem(row_idx, 0, QTableWidgetItem(str(timestamp)))
            
            # Event Type
            event_type = log.get('event_type', '')
            event_item = QTableWidgetItem(event_type)
            self.logs_table.setItem(row_idx, 1, event_item)
            
            # Level (inferred from status/message)
            level = self._infer_level(log)
            level_item = QTableWidgetItem(level)
            
            # Color code by level
            if level == "CRITICAL":
                level_item.setBackground(QColor(255, 200, 200))
            elif level == "ERROR":
                level_item.setBackground(QColor(255, 230, 200))
            elif level == "WARNING":
                level_item.setBackground(QColor(255, 255, 200))
            
            self.logs_table.setItem(row_idx, 2, level_item)
            
            # Username
            username = log.get('username', '')
            self.logs_table.setItem(row_idx, 3, QTableWidgetItem(str(username)))
            
            # Action
            action = log.get('action', '')
            self.logs_table.setItem(row_idx, 4, QTableWidgetItem(str(action)))
            
            # Status
            status = log.get('status', '')
            status_item = QTableWidgetItem(str(status))
            if status == "SUCCESS":
                status_item.setBackground(QColor(200, 255, 200))
            elif status == "FAILED":
                status_item.setBackground(QColor(255, 200, 200))
            self.logs_table.setItem(row_idx, 5, status_item)
            
            # Details - Clean up [SUCCESS]/[FAILED] and Username
            details = log.get('details', '')
            details_clean = self._clean_details(str(details))
            # Truncate long details for display
            details_text = details_clean[:100] + "..." if len(details_clean) > 100 else details_clean
            self.logs_table.setItem(row_idx, 6, QTableWidgetItem(details_text))
        
        # Auto-scroll to newest (top)
        if self.logs_table.rowCount() > 0:
            self.logs_table.scrollToTop()
    
    def _infer_level(self, log: Dict[str, Any]) -> str:
        """Infer log level from log entry"""
        status = str(log.get('status', '')).upper()
        event_type = str(log.get('event_type', '')).upper()
        
        if 'CRITICAL' in status or event_type in ['ERROR']:
            return "CRITICAL"
        elif status in ['ERROR', 'FAILED']:
            return "ERROR"
        elif status == "WARNING":
            return "WARNING"
        else:
            return "INFO"
    
    def _clean_details(self, details: str) -> str:
        """Remove [SUCCESS]/[FAILED] status and Username from details"""
        import re
        # Remove [SUCCESS] or [FAILED] blocks
        details = re.sub(r'\s*\[(?:SUCCESS|FAILED)\]\s*', '', details)
        # Remove "- Username: xxx" pattern
        details = re.sub(r'\s*-\s*Username:\s*\w+', '', details)
        # Remove "Username: xxx" pattern
        details = re.sub(r'\s*Username:\s*\w+', '', details)
        # Clean up extra spaces
        details = re.sub(r'\s+', ' ', details).strip()
        return details
    
    def _on_filter_changed(self) -> None:
        """Handle filter changes"""
        self._refresh_logs()
    
    def _clear_filters(self) -> None:
        """Clear all filters"""
        self.event_filter.setCurrentText("ALL")
        self.level_filter.setCurrentText("ALL")
        self.user_filter.clear()
        self.time_span.setValue(1)
        self.search_box.clear()
    
    def _toggle_auto_refresh(self, state: int) -> None:
        """Toggle auto-refresh"""
        self.auto_refresh = (state == 2)  # 2 is checked state in PyQt6
        
        if self.auto_refresh:
            self._refresh_logs()  # Refresh immediately when enabling
            self.refresh_timer.start(self.refresh_interval)
        else:
            self.refresh_timer.stop()
    
    def _export_to_csv(self) -> None:
        """Export logs to CSV file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Audit Logs",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    if self.current_logs:
                        fieldnames = self.current_logs[0].keys()
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(self.current_logs)
                
                QMessageBox.information(self, "Success", f"Exported {len(self.current_logs)} logs to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Error exporting logs: {str(e)}")
    
    def _show_statistics(self) -> None:
        """Show log statistics"""
        try:
            if not self.current_logs:
                QMessageBox.information(self, "Statistics", "No logs available")
                return
            
            # Calculate statistics
            total_logs = len(self.current_logs)
            event_counts = {}
            status_counts = {"SUCCESS": 0, "FAILED": 0}
            
            for log in self.current_logs:
                event_type = log.get('event_type', 'UNKNOWN')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                status = log.get('status', 'UNKNOWN')
                if status in status_counts:
                    status_counts[status] += 1
            
            # Format statistics message
            stats_msg = f"Total Logs: {total_logs}\n\n"
            stats_msg += "By Event Type:\n"
            for event_type, count in sorted(event_counts.items()):
                stats_msg += f"  {event_type}: {count}\n"
            
            stats_msg += f"\nSuccess/Failed:"
            stats_msg += f"\n  SUCCESS: {status_counts['SUCCESS']}"
            stats_msg += f"\n  FAILED: {status_counts['FAILED']}"
            
            QMessageBox.information(self, "Log Statistics", stats_msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate statistics: {str(e)}")
    
    def closeEvent(self, event) -> None:
        """Clean up on close"""
        self.refresh_timer.stop()
        super().closeEvent(event)

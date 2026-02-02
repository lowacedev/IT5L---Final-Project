from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt

from datetime import datetime, timedelta
from app.views.BaseView import BaseView

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator


class DashboardView(BaseView):  
    def __init__(self, db, user, reports_service=None):
        super().__init__()
        self.db = db
        self.user = user if user else {'username': 'Guest', 'role': 'guest'}
        self.reports_model = reports_service
        self.setObjectName("content_area")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        header = QLabel(f"Welcome back, {user.get('full_name', 'User')}!")
        header.setObjectName("page_title")
        layout.addWidget(header)

        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(12)

        kpi1 = self.make_kpi_card("Today's Sales", "Php 0.00", "SALES", attr_name='kpi_sales_label')
        kpi2 = self.make_kpi_card("Transactions", "0", "TRANS", attr_name='kpi_transactions_label')
        kpi3 = self.make_kpi_card("Total Products", "0", "ITEMS", attr_name='kpi_total_products_label')

        kpi_grid.addWidget(kpi1, 0, 0)
        kpi_grid.addWidget(kpi2, 0, 1)
        kpi_grid.addWidget(kpi3, 0, 2)

        layout.addLayout(kpi_grid)

        charts_container = QHBoxLayout()
        charts_container.setSpacing(4)

        left_chart_frame = QFrame()
        left_chart_frame.setObjectName("chart_frame")
        left_chart_layout = QVBoxLayout(left_chart_frame)
        left_chart_layout.setContentsMargins(10, 10, 10, 10)

        left_chart_title = QLabel("Sales Trend")
        left_chart_title.setObjectName("section_title")
        left_chart_layout.addWidget(left_chart_title)

        
        self.period_selector = QComboBox()
        self.period_selector.addItems(["Daily", "Weekly", "Monthly"])
        self.period_selector.setVisible(False)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setVisible(False)

      
        self.fig_sales = Figure(figsize=(6.5, 3.5), dpi=80)
       
        self.fig_sales.patch.set_facecolor('#FFFFFF')
        self.canvas_sales = FigureCanvas(self.fig_sales)
        self.canvas_sales.setMinimumHeight(450)
        
        try:
            self.canvas_sales.setStyleSheet('background-color: white;')
        except Exception:
            pass
        left_chart_layout.addWidget(self.canvas_sales, 1)

        charts_container.addWidget(left_chart_frame, 1)

        right_chart_frame = QFrame()
        right_chart_frame.setObjectName("chart_frame")
        right_chart_layout = QVBoxLayout(right_chart_frame)
        right_chart_layout.setContentsMargins(50, 10, 10, 10)
        right_chart_layout.setSpacing(10)

        right_chart_title = QLabel("Top Selling Items")
        right_chart_title.setObjectName("section_title")
        right_chart_layout.addWidget(right_chart_title)

        self.fig_items = Figure(figsize=(6.5, 3.5), dpi=80)
        self.fig_items.patch.set_facecolor('#FFFFFF')
        self.canvas_items = FigureCanvas(self.fig_items)
        self.canvas_items.setMinimumHeight(320)
        try:
            self.canvas_items.setMinimumWidth(560)
        except Exception:
            pass
        try:
            self.canvas_items.setStyleSheet('background-color: white;')
        except Exception:
            pass
        right_chart_layout.addWidget(self.canvas_items, 1)

        charts_container.addWidget(right_chart_frame, 1)

        layout.addLayout(charts_container)

        self.setLayout(layout)

    def make_kpi_card(self, title, value, icon, attr_name=None, comparison_attr=None):
        card = QFrame()
        card.setObjectName("kpi_card")
        
        
        card.setMaximumHeight(200)  
        card.setMinimumHeight(100)  
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)  

        title_label = QLabel(title)
        title_label.setObjectName("kpi_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        card_layout.addWidget(title_label)
        
        card_layout.addStretch()

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        value_label = QLabel(value)
        value_label.setObjectName("kpi_value")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        if attr_name:
            setattr(self, attr_name, value_label)
        
        footer_layout.addWidget(value_label)

        card_layout.addLayout(footer_layout)
        
        return card

    def make_action_card(self, icon, title, description):
        """Create an action card widget."""
        card = QFrame()
        card.setObjectName("action_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3B82F6;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: 600; font-size: 14px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #6B7280; font-size: 12px;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)

        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)

        return card

    def load_sales_chart(self, days=30, period=None):
        """Fetch sales data and draw chart with Matplotlib."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days-1)
            start_str = start_date.strftime("%Y-%m-%d")
            end_str = end_date.strftime("%Y-%m-%d")

            # Determine period
            if period is None:
                sel = getattr(self, 'period_selector', None)
                if sel:
                    p = sel.currentText().lower()
                else:
                    p = 'daily'
            else:
                p = period

            data = self.reports_model.get_sales_aggregate(start_str, end_str, period=p)
            # Clear the figure and create a fresh axes to avoid stacking/overlap
            self.fig_sales.clear()
            ax = self.fig_sales.add_subplot(111)

            if not data:
                ax.text(0.5, 0.5, 'No sales data', ha='center', va='center', color='#6B7280', fontsize=14)
                self.canvas_sales.draw()
                return

            labels = [str(r[0]) for r in data]
            totals = [float(r[1]) if r[1] is not None else 0.0 for r in data]

            # Use numeric x positions (avoids categorical axis quirks) and set xtick labels
            x = list(range(len(labels)))
            ax.plot(x, totals, marker='o', color='#3B82F6', linewidth=2.5, markersize=8, label='Revenue')
            ax.fill_between(x, totals, color='#3B82F6', alpha=0.15)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, fontsize=9)
            
            # Styling
            ax.set_title('Sales Trend', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel('Revenue (Php)', fontsize=11, fontweight='bold')
            ax.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
            
            # Format y-axis as currency with sensible tick locator
            ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
            def currency_fmt(x, pos):
                try:
                    x = float(x)
                except Exception:
                    return ''
                if abs(x) >= 1_000_000:
                    return f'Php {x/1_000_000:.1f}M'
                if abs(x) >= 1000:
                    return f'Php {x/1000:.0f}K'
                return f'Php {x:.0f}'
            ax.yaxis.set_major_formatter(FuncFormatter(currency_fmt))
            
            # Improve x-axis labels
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.set_facecolor('#FFFFFF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Apply padding and reasonable subplot margins so labels don't get clipped
            try:
                self.fig_sales.tight_layout(pad=1.6)
                self.fig_sales.subplots_adjust(left=0.12, right=0.98, top=0.88, bottom=0.18)
            except Exception:
                try:
                    self.fig_sales.tight_layout()
                except Exception:
                    pass
            self.canvas_sales.draw()

        except Exception as e:
            print(f"[DASHBOARD] load_sales_chart error: {e}")

    def load_top_items_chart(self):
        """Load and display top-selling items chart with Matplotlib."""
        try:
            data = self.reports_model.get_top_selling_items(limit=10)
            # Clear the figure and create fresh axes to prevent overlapping axes/text
            self.fig_items.clear()
            ax = self.fig_items.add_subplot(111)

            if not data:
                ax.text(0.5, 0.5, 'No sales data', ha='center', va='center', color='#6B7280', fontsize=14)
                self.canvas_items.draw()
                return

            items = [str(r[1])[:30] for r in data]  # Shorter labels for responsive fit
            quantities = [int(r[3]) for r in data]

            y_pos = list(range(len(items)))[::-1]
            colors = ['#10B981' if i % 2 == 0 else '#059669' for i in range(len(items))]
            bars = ax.barh(y_pos, quantities, color=colors, edgecolor='#047857', linewidth=1.2)
            
            # Add value labels on bars
            for i, (bar, qty) in enumerate(zip(bars, quantities)):
                ax.text(qty, bar.get_y() + bar.get_height()/2, f' {qty}', 
                       va='center', fontsize=9, fontweight='bold')
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(items, fontsize=9)
            # Ensure bars don't overflow into neighboring widgets
            if quantities:
                ax.set_xlim(0, max(quantities) * 1.12)
            ax.set_xlabel('Quantity Sold', fontsize=11, fontweight='bold')
            ax.set_title('Top Selling Items (by Qty)', fontsize=14, fontweight='bold', pad=15)
            ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
            ax.set_facecolor('#FFFFFF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', labelsize=9)
            
            # Add slightly larger padding and adjust subplot margins for horizontal bars
            try:
                self.fig_items.tight_layout(pad=1.6)
                # Shift axes to the right inside the figure so y-labels are rendered within canvas
                self.fig_items.subplots_adjust(left=0.32, right=0.98, top=0.88, bottom=0.12)
            except Exception:
                try:
                    self.fig_items.tight_layout()
                except Exception:
                    pass
            self.canvas_items.draw()

        except Exception as e:
            print(f"[DASHBOARD] load_top_items_chart error: {e}")
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QComboBox
from PyQt6.QtCore import Qt

from datetime import datetime, timedelta
from app.models.ReportsModel import ReportsModel

# Matplotlib for static charts
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class DashboardView(QWidget):  # MATPLOTLIB VERSION ONLY
    def __init__(self, db, user):
        super().__init__()
        self.db = db
        self.user = user if user else {'username': 'Guest', 'role': 'guest'}
        self.setObjectName("content_area")

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel(f"Welcome back, {user.get('username', 'User')}!")
        header.setObjectName("page_title")
        layout.addWidget(header)

        # KPI Cards Grid
        kpi_grid = QGridLayout()
        kpi_grid.setSpacing(20)

        # Create KPI cards
        kpi1 = self.make_kpi_card("Today's Sales", "Php 0.00", "SALES", 
                                   attr_name='kpi_sales_label', 
                                   comparison_attr='kpi_sales_comparison_label')
        kpi2 = self.make_kpi_card("Transactions", "0", "TRANS", attr_name='kpi_transactions_label')
        kpi3 = self.make_kpi_card("Total Products", "0", "ITEMS", attr_name='kpi_total_products_label')

        kpi_grid.addWidget(kpi1, 0, 0)
        kpi_grid.addWidget(kpi2, 0, 1)
        kpi_grid.addWidget(kpi3, 0, 2)

        layout.addLayout(kpi_grid)

        # Two-column chart layout
        charts_container = QHBoxLayout()

        # Left chart - Sales Trend
        left_chart_frame = QFrame()
        left_chart_frame.setObjectName("chart_frame")
        left_chart_layout = QVBoxLayout(left_chart_frame)
        left_chart_layout.setContentsMargins(10, 10, 10, 10)

        left_chart_title = QLabel("Sales Trend")
        left_chart_title.setObjectName("section_title")
        left_chart_layout.addWidget(left_chart_title)

        # Period selector (Daily/Weekly/Monthly) - hidden for now
        self.period_selector = QComboBox()
        self.period_selector.addItems(["Daily", "Weekly", "Monthly"])
        self.period_selector.setVisible(False)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setVisible(False)

        # Matplotlib canvas for sales trend - responsive sizing
        self.fig_sales = Figure(figsize=(6.5, 3.5), dpi=80)
        self.fig_sales.patch.set_facecolor('#F9FAFB')
        self.canvas_sales = FigureCanvas(self.fig_sales)
        self.canvas_sales.setMinimumHeight(320)
        left_chart_layout.addWidget(self.canvas_sales, 1)

        charts_container.addWidget(left_chart_frame, 1)

        # Right chart - Top Selling Items
        right_chart_frame = QFrame()
        right_chart_frame.setObjectName("chart_frame")
        right_chart_layout = QVBoxLayout(right_chart_frame)
        right_chart_layout.setContentsMargins(10, 10, 10, 10)
        right_chart_layout.setSpacing(10)

        right_chart_title = QLabel("Top Selling Items")
        right_chart_title.setObjectName("section_title")
        right_chart_layout.addWidget(right_chart_title)

        # Matplotlib canvas for top items - responsive sizing
        self.fig_items = Figure(figsize=(6.5, 3.5), dpi=80)
        self.fig_items.patch.set_facecolor('#F9FAFB')
        self.canvas_items = FigureCanvas(self.fig_items)
        self.canvas_items.setMinimumHeight(320)
        right_chart_layout.addWidget(self.canvas_items, 1)

        charts_container.addWidget(right_chart_frame, 1)

        layout.addLayout(charts_container)

        self.setLayout(layout)

        # Load chart data
        try:
            self.reports_model = ReportsModel()
            self.load_sales_chart()
            self.load_top_items_chart()
        except Exception as e:
            print(f"[DASHBOARD] Failed to initialize reports model: {e}")

    def make_kpi_card(self, title, value, icon, attr_name=None, comparison_attr=None):
        """Create a KPI card widget."""
        card = QFrame()
        card.setObjectName("kpi_card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)

        # Icon and Title
        header_layout = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #3B82F6;")

        title_label = QLabel(title)
        title_label.setObjectName("kpi_title")

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Value
        value_label = QLabel(value)
        value_label.setObjectName("kpi_value")

        # Optionally expose the label on the view for controller updates
        if attr_name:
            setattr(self, attr_name, value_label)

        card_layout.addLayout(header_layout)
        card_layout.addWidget(value_label)
        
        # Comparison label (optional)
        if comparison_attr:
            comparison_label = QLabel("")
            comparison_label.setStyleSheet("font-size: 12px; font-weight: bold;")
            setattr(self, comparison_attr, comparison_label)
            card_layout.addWidget(comparison_label)

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
            ax = self.fig_sales.subplots()
            ax.clear()

            if not data:
                ax.text(0.5, 0.5, 'No sales data', ha='center', va='center', color='#6B7280', fontsize=14)
                self.canvas_sales.draw()
                return

            labels = [str(r[0]) for r in data]
            totals = [float(r[1]) if r[1] is not None else 0.0 for r in data]

            # Enhanced styling
            ax.plot(labels, totals, marker='o', color='#3B82F6', linewidth=2.5, markersize=8, label='Revenue')
            ax.fill_between(range(len(labels)), totals, color='#3B82F6', alpha=0.15)
            
            # Styling
            ax.set_title('Sales Trend', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylabel('Revenue (Php)', fontsize=11, fontweight='bold')
            ax.set_xlabel('Date', fontsize=11, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'Php {x/1000:.0f}K' if x >= 1000 else f'Php {x:.0f}'))
            
            # Improve x-axis labels
            ax.tick_params(axis='x', rotation=45, labelsize=9)
            ax.tick_params(axis='y', labelsize=9)
            ax.set_facecolor('#FFFFFF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            self.fig_sales.tight_layout()
            self.canvas_sales.draw()

        except Exception as e:
            print(f"[DASHBOARD] load_sales_chart error: {e}")

    def load_top_items_chart(self):
        """Load and display top-selling items chart with Matplotlib."""
        try:
            data = self.reports_model.get_top_selling_items(limit=10)
            ax = self.fig_items.subplots()
            ax.clear()

            if not data:
                ax.text(0.5, 0.5, 'No sales data', ha='center', va='center', color='#6B7280', fontsize=14)
                self.canvas_items.draw()
                return

            items = [str(r[1])[:20] for r in data]  # Shorter labels for responsive fit
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
            ax.set_xlabel('Quantity Sold', fontsize=11, fontweight='bold')
            ax.set_title('Top Selling Items (by Qty)', fontsize=14, fontweight='bold', pad=15)
            ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
            ax.set_axisbelow(True)
            ax.set_facecolor('#FFFFFF')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', labelsize=9)
            
            self.fig_items.tight_layout(pad=0.5)
            self.canvas_items.draw()

        except Exception as e:
            print(f"[DASHBOARD] load_top_items_chart error: {e}")
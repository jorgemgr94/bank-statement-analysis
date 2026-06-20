import os
import json
from decimal import Decimal
from collections import defaultdict

def generate_html_report(items, output_file="output/output.html"):
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    category_totals = defaultdict(Decimal)
    category_items = defaultdict(list)
    
    total_charges = Decimal('0')
    total_msi = Decimal('0')
    total_refunds = Decimal('0')
    total_prepayments = Decimal('0')
    previous_balance = Decimal('0')
    
    # First loop: Calculate raw totals for the top summary widgets
    for item in items:
        amt = item['amount']
        if item['type'] == 'previous_balance':
            previous_balance += amt
        elif item['type'] == 'charge':
            total_charges += amt
        elif item['type'] == 'msi':
            total_msi += amt
        elif item['type'] == 'refund':
            total_refunds += amt
        elif item['type'] in ('payment', 'prepayment'):
            total_prepayments += amt

    total_net_calc = previous_balance + total_charges + total_msi + total_refunds + total_prepayments
    
    # Second loop: Populate categories, offsetting previous_balance against payments
    balance_to_offset = previous_balance
    
    for item in items:
        if item['type'] == 'previous_balance':
            continue  # Don't show Adeudo Anterior in categories
            
        amt = item['amount']
        
        # Absorb payments to pay off the Adeudo Anterior first
        if amt < 0 and item['type'] in ('payment', 'prepayment') and balance_to_offset > 0:
            offset = min(abs(amt), balance_to_offset)
            amt += offset
            balance_to_offset -= offset
            
            # If payment was fully absorbed by the previous balance, don't show it
            if abs(amt) < Decimal('0.01'):
                continue
                
        cat = item['category']
        category_totals[cat] += amt
        
        item_copy = dict(item)
        item_copy['amount'] = amt
        category_items[cat].append(item_copy)
    
    # Sort categories descending by amount for the TABLE
    sorted_categories_desc = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # Chart Colors Palette
    CHART_COLORS = [
        '#f43f5e', '#ec4899', '#d946ef', '#a855f7', '#8b5cf6', 
        '#6366f1', '#3b82f6', '#0ea5e9', '#06b6d4', '#14b8a6', 
        '#10b981', '#22c55e', '#84cc16', '#eab308'
    ]

    # Prepare data for Chart.js
    chart_labels = []
    chart_data = []
    
    # Calculate total positive expenses for percentage based on logic
    total_expenses_for_chart = sum(t for c, t in sorted_categories_desc if t > 0)
    
    # Process categories for both Chart (only positive usually) and Table (all)
    table_rows = []
    
    color_index = 0
    for cat, total in sorted_categories_desc:
        # Chart Data (only positive)
        if total > 0:
            chart_labels.append(cat)
            chart_data.append(float(round(total, 2)))
        
        # Table Data (All)
        color = CHART_COLORS[color_index % len(CHART_COLORS)] if total > 0 else '#cbd5e1' # Grey for refunds
        if total > 0:
            color_index += 1
            
        pct = float(total / total_expenses_for_chart * 100) if (total > 0 and total_expenses_for_chart) else 0.0
        
        # Helper for transaction list HTML
        tx_list_html = ""
        for item in sorted(category_items[cat], key=lambda x: x['amount'], reverse=True):
            amt_class = 'text-rose-600' if item['amount'] > 0 else 'text-emerald-600'
            tx_list_html += f"""
                <div class="flex justify-between items-center py-2 border-b border-slate-50 last:border-0 hover:bg-slate-50 px-2 rounded">
                    <div class="flex flex-col">
                        <span class="text-xs text-slate-400 font-mono">{item['date']}</span>
                        <span class="text-sm text-slate-700 font-medium">{item['description']}</span>
                    </div>
                    <span class="font-mono text-sm font-bold {amt_class}">
                        ${item['amount']:,.2f}
                    </span>
                </div>
            """
            
        table_rows.append({
            'cat': cat,
            'total': total,
            'pct': pct,
            'color': color,
            'tx_html': tx_list_html,
            'count': len(category_items[cat])
        })

    # Generate Table HTML
    table_html = ""
    for row in table_rows:
        pct_display = f"{row['pct']:.1f}%" if row['pct'] > 0 else '-'
        total_class = 'text-rose-600' if row['total'] > 0 else 'text-emerald-600'
        
        table_html += f"""
        <tr class="hover:bg-slate-50 cursor-pointer group transition-colors" onclick="openModal('{row['cat']}')">
            <td class="px-4 py-3">
                <div class="flex items-center space-x-3">
                    <div class="w-2.5 h-2.5 rounded-full ring-2 ring-white shadow-sm" style="background-color: {row['color']}"></div>
                    <span class="font-medium text-slate-700 text-sm group-hover:text-slate-900">{row['cat']} <span class="text-xs text-slate-400 font-normal">({row['count']})</span></span>
                </div>
            </td>
            <td class="px-4 py-3 text-right text-xs text-slate-500 font-mono">
                {pct_display}
            </td>
            <td class="px-4 py-3 text-right font-mono text-sm font-bold {total_class}">
                ${row['total']:,.2f}
            </td>
            <td class="px-4 py-3 text-center" onclick="event.stopPropagation()">
                <button onclick="copyToClipboard('{row['total']:.2f}')" 
                        class="p-1.5 text-slate-300 hover:text-indigo-600 hover:bg-indigo-50 rounded transition-all"
                        title="Copiar monto">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"></path></svg>
                </button>
            </td>
        </tr>
        """

    # Generate Hidden Modals HTML
    modals_html = ""
    for row in table_rows:
        modals_html += f"""
        <div id="data-{row['cat']}" class="hidden">
            {row['tx_html']}
        </div>
        """

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Gastos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .hide-scroll::-webkit-scrollbar {{ display: none; }}
        .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen pb-10">
    <div class="max-w-6xl mx-auto px-4 pt-8">
        <!-- R1: Titulo -->
        <header class="mb-6 flex justify-between items-end border-b border-slate-200 pb-4">
            <div>
                <h1 class="text-2xl font-bold tracking-tight text-slate-800">Dashboard Financiero</h1>
                <p class="text-sm text-slate-500">Resumen mensual de movimientos</p>
            </div>
            <div class="text-right">
                <p class="text-xs text-slate-400 uppercase tracking-wider">Total a Pagar</p>
                <p class="text-3xl font-bold text-slate-900">${total_net_calc:,.2f}</p>
            </div>
        </header>

        <!-- R2: Widgets Compactos -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Adeudo Anterior</p>
                <p class="text-lg font-bold text-slate-700">${previous_balance:,.2f}</p>
            </div>
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Cargos Mes</p>
                <p class="text-lg font-bold text-rose-600">${total_charges:,.2f}</p>
            </div>
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Mensualidades</p>
                <p class="text-lg font-bold text-rose-500">${total_msi:,.2f}</p>
            </div>
            <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-100 flex flex-col justify-between">
                <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Pagos / Abonos</p>
                <p class="text-lg font-bold text-emerald-600">-${abs(total_refunds + total_prepayments):,.2f}</p>
            </div>
        </div>

        <!-- R3: Grafica + Tabla (Split View) -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[600px]">
            
            <!-- Izquierda: Chart -->
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 flex flex-col justify-center items-center relative">
                <h3 class="absolute top-6 left-6 text-sm font-semibold text-slate-700">Distribución de Gastos</h3>
                <div class="w-full h-full max-h-[400px]">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>

            <!-- Derecha: Tabla de Categorias -->
            <div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col overflow-hidden">                
                <div class="overflow-y-auto flex-1 p-0">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-slate-50 sticky top-0 z-10 text-xs text-slate-500 uppercase font-semibold tracking-wider">
                            <tr>
                                <th class="px-4 py-3">Categoría</th>
                                <th class="px-4 py-3 text-right">%</th>
                                <th class="px-4 py-3 text-right">Monto</th>
                                <th class="px-4 py-3 text-center">Copiar</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-50">
                            {table_html}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Hidden Data Containers for Modal -->
    {modals_html}

    <!-- Modal Backdrop -->
    <div id="modal-backdrop" class="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-40 hidden transition-opacity opacity-0" onclick="closeModal()"></div>

    <!-- Modal Content -->
    <div id="modal-panel" class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white w-full max-w-lg rounded-2xl shadow-2xl z-50 hidden transition-all scale-95 opacity-0 overflow-hidden flex flex-col max-h-[80vh]">

        <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
            <h3 id="modal-title" class="text-lg font-bold text-slate-800">Detalles</h3>
            <button onclick="closeModal()" class="text-slate-400 hover:text-slate-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
        <div id="modal-body" class="p-6 overflow-y-auto flex-1">
            <!-- Content Injected via JS -->
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="fixed bottom-8 left-1/2 -translate-x-1/2 bg-slate-900 text-white px-4 py-2 rounded-full text-xs font-medium shadow-2xl opacity-0 translate-y-4 transition-all duration-300 pointer-events-none flex items-center space-x-2 z-50">
        <svg class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
        <span id="toast-msg">Copiado</span>
    </div>

    <script>
        // --- Modal Logic ---
        const scrollLockClass = 'overflow-hidden';
        const backdrop = document.getElementById('modal-backdrop');
        const panel = document.getElementById('modal-panel');
        const title = document.getElementById('modal-title');
        const body = document.getElementById('modal-body');

        function openModal(category) {{
            const content = document.getElementById('data-' + category).innerHTML;
            title.textContent = category;
            body.innerHTML = content;
            
            backdrop.classList.remove('hidden');
            panel.classList.remove('hidden');
            
            // Animation frame
            requestAnimationFrame(() => {{
                backdrop.classList.remove('opacity-0');
                panel.classList.remove('scale-95', 'opacity-0');
            }});
            
            document.body.classList.add(scrollLockClass);
        }}

        function closeModal() {{
            backdrop.classList.add('opacity-0');
            panel.classList.add('scale-95', 'opacity-0');
            
            setTimeout(() => {{
                backdrop.classList.add('hidden');
                panel.classList.add('hidden');
                document.body.classList.remove(scrollLockClass);
            }}, 200);
        }}
        
        // Close on Escape
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});


        // --- Chart Logic ---
        const ctx = document.getElementById('categoryChart').getContext('2d');
        const chartData = {{
            labels: {json.dumps(chart_labels)},
            datasets: [{{
                data: {json.dumps(chart_data)},
                backgroundColor: {json.dumps(CHART_COLORS)},
                borderWidth: 0,
                hoverOffset: 10,
                offset: 5
            }}]
        }};

        new Chart(ctx, {{
            type: 'doughnut',
            data: chartData,
            options: {{
                cutout: '75%',
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: '#1e293b',
                        padding: 12,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {{
                            label: function(context) {{
                                return ' $' + context.parsed.toLocaleString('en-US', {{minimumFractionDigits: 2}});
                            }}
                        }}
                    }}
                }},
                responsive: true,
                maintainAspectRatio: false,
                layout: {{
                    padding: 20
                }}
            }}
        }});

        // --- Utils ---
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                showToast(`Monto copiado: $${{text}}`);
            }});
        }}

        function showToast(msgText) {{
            const toast = document.getElementById('toast');
            const msg = document.getElementById('toast-msg');
            msg.textContent = msgText;
            toast.classList.remove('opacity-0', 'translate-y-4');
            setTimeout(() => {{
                toast.classList.add('opacity-0', 'translate-y-4');
            }}, 2000);
        }}
    </script>
</body>
</html>
    """
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Reporte HTML generado en: {output_file}")

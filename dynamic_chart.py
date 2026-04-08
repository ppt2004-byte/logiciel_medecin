import webbrowser
import os
import json
from database import Database

def generate_and_open_chart(periode="Tout"):
    db = Database()
    total, stats_type, stats_paiement = db.get_stats(periode)
    paiement_details = db.get_paiement_details(periode)
    
    # Préparation des données pour un graphique Sunburst (très fluide et animé)
    sunburst_data = []
    
    # On regroupe les détails par moyen de paiement
    for mp_stat in stats_paiement:
        mp_name = mp_stat["_id"]
        mp_total = mp_stat["count"]
        
        children = []
        for d in paiement_details:
            if d["moyen_paiement"] == mp_name:
                children.append({
                    "name": d["type_patient"],
                    "value": d["count"]
                })
                
        sunburst_data.append({
            "name": mp_name,
            "value": mp_total,
            "children": children
        })
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tableau de Bord Dynamique & Fluide</title>
        <!-- Utilisation de Apache ECharts pour des animations très fluides -->
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f5f7; margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; }}
            .header {{ text-align: center; padding: 20px; background-color: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); z-index: 10; }}
            .header h1 {{ margin: 0; color: #1f538d; font-size: 28px; }}
            .header h2 {{ margin: 5px 0 0 0; color: #7f8c8d; font-size: 18px; font-weight: normal; }}
            .chart-container {{ flex-grow: 1; padding: 20px; display: flex; justify-content: center; align-items: center; }}
            #mainChart {{ width: 100%; max-width: 1000px; height: 100%; min-height: 600px; background: white; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Répartition des Paiements & Motifs de Consultation</h1>
            <h2>Période : {periode} | Total Patients : {total}</h2>
        </div>
        
        <div class="chart-container">
            <div id="mainChart"></div>
        </div>

        <script>
            var chartDom = document.getElementById('mainChart');
            var myChart = echarts.init(chartDom);
            var option;

            const data = {json.dumps(sunburst_data)};

            option = {{
                tooltip: {{
                    trigger: 'item',
                    formatter: function (info) {{
                        var value = info.value;
                        var name = info.name;
                        return '<div style="font-weight:bold;font-size:16px;padding:5px;">' + name + ' : ' + value + ' consultations</div>';
                    }}
                }},
                series: {{
                    type: 'sunburst',
                    data: data,
                    radius: ['20%', '90%'],
                    itemStyle: {{
                        borderRadius: 7,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }},
                    label: {{
                        show: true,
                        formatter: '{{b}}\\n{{c}}',
                        fontSize: 14,
                        fontWeight: 'bold',
                        color: '#fff',
                        textBorderColor: 'transparent',
                        textShadowColor: 'rgba(0,0,0,0.3)',
                        textShadowBlur: 3
                    }},
                    emphasis: {{
                        focus: 'ancestor',
                        itemStyle: {{
                            shadowBlur: 20,
                            shadowColor: 'rgba(0, 0, 0, 0.4)'
                        }}
                    }},
                    levels: [
                        {{}}, // Blank for root
                        {{ // Moyens de paiement
                            r0: '10%',
                            r: '45%',
                            itemStyle: {{ borderWidth: 3 }},
                            label: {{ position: 'inner', rotate: 'tangential' }}
                        }},
                        {{ // Types de patients
                            r0: '47%',
                            r: '85%',
                            label: {{ position: 'inner', fontSize: 12, rotate: 'tangential' }},
                            itemStyle: {{ borderWidth: 2, opacity: 0.8 }}
                        }}
                    ],
                    // Couleurs vives
                    color: ['#FF5733', '#3498DB', '#2ECC71', '#F1C40F', '#9B59B6', '#E67E22', '#E74C3C', '#1ABC9C']
                }}
            }};

            option && myChart.setOption(option);
            
            // Redimensionnement fluide
            window.addEventListener('resize', function() {{
                myChart.resize();
            }});
        </script>
    </body>
    </html>
    """
    
    file_path = os.path.join(os.getcwd(), "dashboard_fluide.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    webbrowser.open('file://' + os.path.realpath(file_path))
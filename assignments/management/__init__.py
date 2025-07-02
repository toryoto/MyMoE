from django.core.management.base import BaseCommand
from assignments.models import Client, Project
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'クライアントとプロジェクトの初期データを作成します'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('クライアント・プロジェクトデータを作成中...'))

        # クライアントとプロジェクトのデータ定義
        clients_data = [
            {
                'name': 'みずほ銀行',
                'contact_person': '田中太郎',
                'industry': '金融',
                'projects': [
                    {'name': 'インターネットバンキング刷新', 'months': 12},
                    {'name': 'AI与信システム構築', 'months': 8},
                    {'name': 'モバイルアプリ開発', 'months': 6},
                ]
            },
            {
                'name': '日産自動車',
                'contact_person': '佐藤花子',
                'industry': '自動車',
                'projects': [
                    {'name': 'ERP基盤更改プロジェクト', 'months': 18},
                    {'name': 'コネクテッドカーシステム開発', 'months': 10},
                    {'name': 'グローバル販売管理システム', 'months': 15},
                ]
            },
            {
                'name': 'セブン&アイ・ホールディングス',
                'contact_person': '鈴木一郎',
                'industry': '小売',
                'projects': [
                    {'name': 'オムニチャネル基盤構築', 'months': 14},
                    {'name': 'POSシステム更新', 'months': 7},
                    {'name': 'EC物流システム最適化', 'months': 9},
                ]
            },
            {
                'name': 'NTT',
                'contact_person': '高橋美咲',
                'industry': '通信',
                'projects': [
                    {'name': '5Gネットワーク管理システム', 'months': 20},
                    {'name': 'クラウド基盤移行プロジェクト', 'months': 12},
                    {'name': 'IoTプラットフォーム開発', 'months': 16},
                ]
            },
            {
                'name': 'JR東日本',
                'contact_person': '山田次郎',
                'industry': '鉄道業',
                'projects': [
                    {'name': '駅務システム刷新', 'months': 11},
                    {'name': 'MaaS連携プラットフォーム', 'months': 13},
                    {'name': '運行管理システム高度化', 'months': 17},
                ]
            },
        ]

        # データ作成
        created_clients = 0
        created_projects = 0

        for client_data in clients_data:
            # クライアント作成
            client, created = Client.objects.get_or_create(
                name=client_data['name'],
                defaults={
                    'contact_person': client_data['contact_person'],
                    'industry': client_data['industry'],
                    'is_active': True
                }
            )
            
            if created:
                created_clients += 1
                self.stdout.write(f'✓ クライアント作成: {client.name}')
            else:
                self.stdout.write(f'- クライアント存在: {client.name}')

            # プロジェクト作成
            for i, project_data in enumerate(client_data['projects']):
                # プロジェクトの開始日を調整（重複を避けるため）
                start_date = date.today() - timedelta(days=30 * i)
                end_date = start_date + timedelta(days=30 * project_data['months'])
                
                project, created = Project.objects.get_or_create(
                    client=client,
                    name=project_data['name'],
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'status': 'active'
                    }
                )
                
                if created:
                    created_projects += 1
                    self.stdout.write(f'  ✓ プロジェクト作成: {project.name}')
                else:
                    self.stdout.write(f'  - プロジェクト存在: {project.name}')

        # 結果レポート
        self.stdout.write(self.style.SUCCESS('\n=== 作成完了 ==='))
        self.stdout.write(f'新規クライアント: {created_clients}件')
        self.stdout.write(f'新規プロジェクト: {created_projects}件')
        self.stdout.write(f'総クライアント数: {Client.objects.count()}件')
        self.stdout.write(f'総プロジェクト数: {Project.objects.count()}件')
        self.stdout.write(self.style.SUCCESS('データ作成が完了しました！'))
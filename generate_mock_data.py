#!/usr/bin/env python3
"""
Generate large mock datasets for S3 Data Lake MCP Server demo.
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import pyarrow as pa
import pyarrow.parquet as pq

fake = Faker()
Faker.seed(42)  # For reproducible data
np.random.seed(42)
random.seed(42)

def generate_customer_analytics_csv(num_records=50000):
    """Generate large customer analytics CSV dataset."""
    print(f"Generating {num_records:,} customer analytics records...")
    
    # Generate realistic customer data
    data = []
    
    # Customer segments
    segments = ['Premium', 'Standard', 'Basic', 'Enterprise']
    regions = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa']
    industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Education', 'Government']
    
    for i in range(num_records):
        # Generate customer profile
        customer_id = f"CUST_{i+1:06d}"
        company_name = fake.company()
        
        # Realistic business metrics
        segment = np.random.choice(segments, p=[0.15, 0.35, 0.35, 0.15])  # Weighted distribution
        region = np.random.choice(regions, p=[0.3, 0.25, 0.2, 0.15, 0.1])
        industry = np.random.choice(industries)
        
        # Revenue based on segment
        if segment == 'Enterprise':
            annual_revenue = np.random.lognormal(15, 1)  # $1M-$50M+
        elif segment == 'Premium':
            annual_revenue = np.random.lognormal(13, 0.8)  # $100K-$5M
        elif segment == 'Standard':
            annual_revenue = np.random.lognormal(11, 0.6)  # $10K-$500K
        else:  # Basic
            annual_revenue = np.random.lognormal(9, 0.5)   # $1K-$50K
        
        # Customer metrics
        employees = max(1, int(np.random.lognormal(4, 1.5)))
        satisfaction_score = np.random.beta(8, 2) * 10  # Skewed towards higher satisfaction
        churn_risk = np.random.beta(2, 8)  # Skewed towards lower churn risk
        
        # Engagement metrics
        monthly_active_users = max(1, int(employees * np.random.uniform(0.3, 1.2)))
        support_tickets = np.random.poisson(2 if segment in ['Premium', 'Enterprise'] else 1)
        
        # Financial metrics
        monthly_spend = annual_revenue / 12 * np.random.uniform(0.8, 1.2)
        lifetime_value = annual_revenue * np.random.uniform(2, 8)
        
        # Dates
        signup_date = fake.date_between(start_date='-3y', end_date='today')
        last_activity = fake.date_between(start_date=signup_date, end_date='today')
        
        data.append({
            'customer_id': customer_id,
            'company_name': company_name,
            'segment': segment,
            'region': region,
            'industry': industry,
            'annual_revenue': round(annual_revenue, 2),
            'employees': employees,
            'satisfaction_score': round(satisfaction_score, 2),
            'churn_risk_score': round(churn_risk, 3),
            'monthly_active_users': monthly_active_users,
            'support_tickets_last_month': support_tickets,
            'monthly_spend': round(monthly_spend, 2),
            'estimated_lifetime_value': round(lifetime_value, 2),
            'signup_date': signup_date.isoformat(),
            'last_activity_date': last_activity.isoformat(),
            'contact_email': fake.company_email(),
            'phone': fake.phone_number(),
            'address': fake.address().replace('\n', ', '),
            'website': f"https://www.{company_name.lower().replace(' ', '').replace(',', '').replace('.', '')}.com"
        })
    
    df = pd.DataFrame(data)
    df.to_csv('customer_analytics.csv', index=False)
    print(f"✅ Generated customer_analytics.csv ({len(df):,} records, {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB)")
    return df

def generate_sales_transactions_json(num_records=75000):
    """Generate large sales transactions JSON dataset."""
    print(f"Generating {num_records:,} sales transaction records...")
    
    products = [
        {'id': 'PROD_001', 'name': 'Enterprise Analytics Platform', 'category': 'Software', 'base_price': 50000},
        {'id': 'PROD_002', 'name': 'Data Integration Suite', 'category': 'Software', 'base_price': 25000},
        {'id': 'PROD_003', 'name': 'AI/ML Consulting', 'category': 'Services', 'base_price': 15000},
        {'id': 'PROD_004', 'name': 'Cloud Migration Service', 'category': 'Services', 'base_price': 30000},
        {'id': 'PROD_005', 'name': 'Security Audit', 'category': 'Services', 'base_price': 8000},
        {'id': 'PROD_006', 'name': 'Training Program', 'category': 'Education', 'base_price': 5000},
        {'id': 'PROD_007', 'name': 'Support Package Premium', 'category': 'Support', 'base_price': 12000},
        {'id': 'PROD_008', 'name': 'Custom Development', 'category': 'Services', 'base_price': 75000},
    ]
    
    sales_reps = [f"REP_{i:03d}" for i in range(1, 51)]  # 50 sales reps
    
    transactions = []
    
    for i in range(num_records):
        transaction_id = f"TXN_{i+1:08d}"
        
        # Select random product and sales rep
        product = random.choice(products)
        sales_rep = random.choice(sales_reps)
        
        # Generate realistic transaction details
        quantity = np.random.poisson(2) + 1  # At least 1
        discount_rate = np.random.beta(2, 8) * 0.3  # 0-30% discount, skewed low
        
        unit_price = product['base_price'] * (1 - discount_rate)
        total_amount = unit_price * quantity
        
        # Transaction date (last 2 years)
        transaction_date = fake.date_time_between(start_date='-2y', end_date='now')
        
        # Payment and status
        payment_methods = ['Credit Card', 'Bank Transfer', 'Check', 'ACH']
        statuses = ['Completed', 'Pending', 'Cancelled', 'Refunded']
        status_weights = [0.85, 0.08, 0.04, 0.03]
        
        status = np.random.choice(statuses, p=status_weights)
        payment_method = random.choice(payment_methods)
        
        # Customer info (referencing our customer dataset)
        customer_id = f"CUST_{random.randint(1, 50000):06d}"
        
        # Commission calculation
        commission_rate = 0.05 if product['category'] == 'Software' else 0.08
        commission = total_amount * commission_rate if status == 'Completed' else 0
        
        transaction = {
            'transaction_id': transaction_id,
            'customer_id': customer_id,
            'product_id': product['id'],
            'product_name': product['name'],
            'product_category': product['category'],
            'sales_rep_id': sales_rep,
            'transaction_date': transaction_date.isoformat(),
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'discount_rate': round(discount_rate, 4),
            'total_amount': round(total_amount, 2),
            'payment_method': payment_method,
            'status': status,
            'commission_amount': round(commission, 2),
            'notes': fake.sentence() if random.random() < 0.3 else None,
            'metadata': {
                'source_system': random.choice(['CRM', 'E-commerce', 'Direct Sales']),
                'channel': random.choice(['Online', 'Phone', 'In-Person', 'Partner']),
                'campaign_id': f"CAMP_{random.randint(1, 100):03d}" if random.random() < 0.4 else None,
                'processed_by': fake.name(),
                'processing_time_ms': random.randint(50, 2000)
            }
        }
        
        transactions.append(transaction)
    
    # Create the final JSON structure
    dataset = {
        'metadata': {
            'dataset_name': 'sales_transactions',
            'version': '2.1.0',
            'generated_date': datetime.now().isoformat(),
            'record_count': len(transactions),
            'description': 'Comprehensive sales transaction dataset for analytics and reporting',
            'schema_version': '1.0',
            'data_classification': 'Internal',
            'retention_policy': '7_years'
        },
        'summary_statistics': {
            'total_transactions': len(transactions),
            'date_range': {
                'start': min(t['transaction_date'] for t in transactions),
                'end': max(t['transaction_date'] for t in transactions)
            },
            'total_revenue': sum(t['total_amount'] for t in transactions if t['status'] == 'Completed'),
            'unique_customers': len(set(t['customer_id'] for t in transactions)),
            'unique_products': len(set(t['product_id'] for t in transactions))
        },
        'transactions': transactions
    }
    
    with open('sales_transactions.json', 'w') as f:
        json.dump(dataset, f, indent=2)
    
    print(f"✅ Generated sales_transactions.json ({len(transactions):,} records, {len(json.dumps(dataset)) / 1024 / 1024:.1f} MB)")
    return dataset

def generate_iot_sensor_parquet(num_records=100000):
    """Generate large IoT sensor data in Parquet format."""
    print(f"Generating {num_records:,} IoT sensor records...")
    
    # Sensor configuration
    sensor_types = ['temperature', 'humidity', 'pressure', 'vibration', 'light', 'motion']
    locations = ['Factory_Floor_A', 'Factory_Floor_B', 'Warehouse_North', 'Warehouse_South', 'Office_Building']
    
    # Generate sensor IDs
    sensors = []
    for location in locations:
        for sensor_type in sensor_types:
            for i in range(1, 6):  # 5 sensors of each type per location
                sensors.append({
                    'sensor_id': f"{location}_{sensor_type}_{i:02d}",
                    'sensor_type': sensor_type,
                    'location': location,
                    'installation_date': fake.date_between(start_date='-2y', end_date='-6m')
                })
    
    # Generate time series data
    data = []
    start_time = datetime.now() - timedelta(days=30)  # Last 30 days
    
    for i in range(num_records):
        sensor = random.choice(sensors)
        
        # Generate timestamp (every 5 minutes on average)
        timestamp = start_time + timedelta(minutes=random.randint(0, 30*24*60))
        
        # Generate realistic sensor values based on type
        if sensor['sensor_type'] == 'temperature':
            # Temperature in Celsius, with daily cycles and noise
            hour = timestamp.hour
            base_temp = 20 + 10 * np.sin((hour - 6) * np.pi / 12)  # Daily cycle
            value = base_temp + np.random.normal(0, 2)
            unit = '°C'
            normal_range = (15, 35)
        elif sensor['sensor_type'] == 'humidity':
            # Humidity percentage
            value = max(0, min(100, np.random.normal(45, 15)))
            unit = '%'
            normal_range = (30, 70)
        elif sensor['sensor_type'] == 'pressure':
            # Atmospheric pressure in hPa
            value = np.random.normal(1013.25, 10)
            unit = 'hPa'
            normal_range = (980, 1050)
        elif sensor['sensor_type'] == 'vibration':
            # Vibration in m/s²
            value = abs(np.random.exponential(0.5))
            unit = 'm/s²'
            normal_range = (0, 2)
        elif sensor['sensor_type'] == 'light':
            # Light in lux
            hour = timestamp.hour
            if 6 <= hour <= 18:  # Daylight hours
                value = np.random.lognormal(8, 1)  # Bright
            else:
                value = np.random.lognormal(4, 1)  # Dim
            unit = 'lux'
            normal_range = (0, 10000)
        else:  # motion
            # Motion detection (binary with some analog intensity)
            value = np.random.exponential(0.1) if random.random() < 0.1 else 0
            unit = 'motion_units'
            normal_range = (0, 1)
        
        # Determine if reading is anomalous
        is_anomaly = (value < normal_range[0] or value > normal_range[1])
        
        # Quality score (lower for anomalies)
        quality_score = np.random.beta(8, 2) if not is_anomaly else np.random.beta(2, 8)
        
        data.append({
            'timestamp': timestamp,
            'sensor_id': sensor['sensor_id'],
            'sensor_type': sensor['sensor_type'],
            'location': sensor['location'],
            'value': round(value, 3),
            'unit': unit,
            'quality_score': round(quality_score, 3),
            'is_anomaly': is_anomaly,
            'battery_level': round(np.random.uniform(0.1, 1.0), 3),
            'signal_strength': round(np.random.uniform(-80, -30), 1),  # dBm
            'firmware_version': f"v{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            'maintenance_due': fake.date_between(start_date='today', end_date='+1y').isoformat()
        })
    
    # Convert to DataFrame and save as Parquet
    df = pd.DataFrame(data)
    
    # Optimize data types for Parquet
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['sensor_id'] = df['sensor_id'].astype('category')
    df['sensor_type'] = df['sensor_type'].astype('category')
    df['location'] = df['location'].astype('category')
    df['unit'] = df['unit'].astype('category')
    df['is_anomaly'] = df['is_anomaly'].astype('bool')
    df['firmware_version'] = df['firmware_version'].astype('category')
    
    # Save with compression
    df.to_parquet('iot_sensor_data.parquet', compression='snappy', index=False)
    
    print(f"✅ Generated iot_sensor_data.parquet ({len(df):,} records, {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB)")
    return df

if __name__ == "__main__":
    print("🚀 Generating Mock Datasets for S3 Data Lake MCP Demo")
    print("=" * 60)
    
    # Generate all three datasets
    csv_df = generate_customer_analytics_csv(50000)
    json_data = generate_sales_transactions_json(75000)
    parquet_df = generate_iot_sensor_parquet(100000)
    
    print("\n📊 Dataset Summary:")
    print(f"📄 CSV: {len(csv_df):,} customer records")
    print(f"📋 JSON: {len(json_data['transactions']):,} transaction records")
    print(f"📈 Parquet: {len(parquet_df):,} IoT sensor readings")
    print("\n✅ All datasets generated successfully!")
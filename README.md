# Data Engineering Zoomcamp 2026 - Homework 1

## Question 1: Understanding Docker images

**Task:** Run docker with the python:3.13 image in an interactive bash shell and find the pip version.

**What I did:**
I ran the Docker container with an interactive bash entrypoint to access the container's shell and check the pip version.
```bash
docker run -it --entrypoint bash python:3.13
pip --version
```

**Answer: 25.3**

---

## Question 2: Understanding Docker networking and docker-compose

**Task:** Given the docker-compose.yaml configuration, determine the hostname and port that pgadmin should use to connect to the postgres database.

**What I did:**
I analyzed the docker-compose.yaml file. In Docker Compose, containers on the same network communicate using the service name as the hostname. The postgres service is named `db`, and internally it uses port 5432 (the container port), not the host-mapped port 5433.

**Answer: db:5432**

---

## Data Preparation

Before solving the SQL questions, I downloaded the required datasets:
```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

I then loaded the data into PostgreSQL using the following Python script:
```python
import pandas as pd
from sqlalchemy import create_engine

# Create database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5433/ny_taxi')

# Load green taxi data
df_green = pd.read_parquet('green_tripdata_2025-11.parquet')
df_green.to_sql('green_taxi_trips', engine, if_exists='replace', index=False, chunksize=10000)

# Load zone lookup
df_zones = pd.read_csv('taxi_zone_lookup.csv')
df_zones.to_sql('taxi_zones', engine, if_exists='replace', index=False)

print("Data loaded successfully!")
```

---

## Question 3: Counting short trips

**Task:** For trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), count how many trips had a trip_distance of less than or equal to 1 mile.

**What I did:**
I wrote a SQL query to count all trips in November 2025 where the trip distance was 1 mile or less. I used the >= and < operators to ensure the date range was inclusive of November 1st but exclusive of December 1st.
```sql
SELECT COUNT(*) 
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

**Answer: 8,007**

---

## Question 4: Longest trip for each day

**Task:** Find the pick up day with the longest trip distance. Only consider trips with trip_distance less than 100 miles to exclude data errors.

**What I did:**
I grouped the trips by the pickup date and found the maximum trip distance for each day. I filtered out trips with distances of 100 miles or more to exclude potential errors, then ordered by maximum distance in descending order to find the day with the longest trip.
```sql
SELECT DATE(lpep_pickup_datetime) as pickup_day, 
       MAX(trip_distance) as max_distance
FROM green_taxi_trips
WHERE trip_distance < 100
  AND lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY max_distance DESC
LIMIT 1;
```

**Answer: 2025-11-14**

---

## Question 5: Biggest pickup zone

**Task:** Find the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025.

**What I did:**
I joined the green_taxi_trips table with the taxi_zones table on the pickup location ID. I filtered for trips on November 18th, 2025, then grouped by zone name and summed the total_amount for each zone. Finally, I ordered by the sum in descending order to find the zone with the highest total.
```sql
SELECT tz."Zone", 
       SUM(gt.total_amount) as total
FROM green_taxi_trips gt
JOIN taxi_zones tz ON gt."PULocationID" = tz."LocationID"
WHERE DATE(gt.lpep_pickup_datetime) = '2025-11-18'
GROUP BY tz."Zone"
ORDER BY total DESC
LIMIT 1;
```

**Answer: East Harlem North**

---

## Question 6: Largest tip

**Task:** For passengers picked up in the zone "East Harlem North" in November 2025, find the drop off zone that had the largest tip.

**What I did:**
I performed a double join: one join to match the pickup location with "East Harlem North" and another join to get the drop-off zone name. I filtered for pickups in November 2025 from East Harlem North, then ordered by tip amount in descending order to find the drop-off zone with the largest tip.
```sql
SELECT tz_dropoff."Zone", 
       gt.tip_amount
FROM green_taxi_trips gt
JOIN taxi_zones tz_pickup ON gt."PULocationID" = tz_pickup."LocationID"
JOIN taxi_zones tz_dropoff ON gt."DOLocationID" = tz_dropoff."LocationID"
WHERE tz_pickup."Zone" = 'East Harlem North'
  AND gt.lpep_pickup_datetime >= '2025-11-01' 
  AND gt.lpep_pickup_datetime < '2025-12-01'
ORDER BY gt.tip_amount DESC
LIMIT 1;
```

**Answer: Yorkville West**

---

## Question 7: Terraform Workflow

**Task:** Identify the correct sequence of Terraform commands for: downloading provider plugins and setting up backend, generating proposed changes and auto-executing the plan, and removing all resources managed by Terraform.

**What I did:**
I analyzed the Terraform workflow:
- `terraform init` - Downloads provider plugins and sets up the backend
- `terraform apply -auto-approve` - Generates the execution plan and automatically applies it without manual confirmation
- `terraform destroy` - Removes all resources managed by Terraform

**Answer: terraform init, terraform apply -auto-approve, terraform destroy**

---

## Technologies Used
- Docker & Docker Compose
- PostgreSQL 17
- Python 3.13
- pandas
- SQLAlchemy
- Terraform

## Repository Structure
```
homework/
├── README.md           # This file with all solutions
├── ingest_data.py      # Python script to load data into PostgreSQL
├── queries.sql         # All SQL queries used
└── .gitignore          # Git ignore file
```
EOF

# 3. Create ingest_data.py
cat > ingest_data.py << 'EOF'
import pandas as pd
from sqlalchemy import create_engine

# Create database connection
engine = create_engine('postgresql://postgres:postgres@localhost:5433/ny_taxi')

# Load green taxi data
df_green = pd.read_parquet('green_tripdata_2025-11.parquet')
df_green.to_sql('green_taxi_trips', engine, if_exists='replace', index=False, chunksize=10000)

# Load zone lookup
df_zones = pd.read_csv('taxi_zone_lookup.csv')
df_zones.to_sql('taxi_zones', engine, if_exists='replace', index=False)

print("Data loaded successfully!")
EOF

# 4. Create queries.sql
cat > queries.sql << 'EOF'
-- Question 3: Counting short trips
SELECT COUNT(*) 
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;

-- Question 4: Longest trip for each day
SELECT DATE(lpep_pickup_datetime) as pickup_day, 
       MAX(trip_distance) as max_distance
FROM green_taxi_trips
WHERE trip_distance < 100
  AND lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY max_distance DESC
LIMIT 1;

-- Question 5: Biggest pickup zone
SELECT tz."Zone", SUM(gt.total_amount) as total
FROM green_taxi_trips gt
JOIN taxi_zones tz ON gt."PULocationID" = tz."LocationID"
WHERE DATE(gt.lpep_pickup_datetime) = '2025-11-18'
GROUP BY tz."Zone"
ORDER BY total DESC
LIMIT 1;

-- Question 6: Largest tip
SELECT tz_dropoff."Zone", gt.tip_amount
FROM green_taxi_trips gt
JOIN taxi_zones tz_pickup ON gt."PULocationID" = tz_pickup."LocationID"
JOIN taxi_zones tz_dropoff ON gt."DOLocationID" = tz_dropoff."LocationID"
WHERE tz_pickup."Zone" = 'East Harlem North'
  AND gt.lpep_pickup_datetime >= '2025-11-01' 
  AND gt.lpep_pickup_datetime < '2025-12-01'
ORDER BY gt.tip_amount DESC
LIMIT 1;

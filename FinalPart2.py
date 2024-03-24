import pandas as pd
from sqlalchemy import create_engine
import warnings
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

#Remove Warnings
warnings.filterwarnings('ignore', category=pd.core.generic.SettingWithCopyWarning)

# Connection string for your SQL database
#Manually generate one for yourself if required
#Insert your username, password, host and database name
connection_string = ""

#For reading the data from a url
url = 'https://raw.githubusercontent.com/DarcyZeng1/HouseData/main/Bangalore.csv'



df= pd.read_csv(url)

#How many Rows prior to cleaning
print("Before cleaning", len(df))

#According to the information about the data, "Since for a set of houses, nothing was mentioned about certain amenities, '9' was used to mark such values, which could indicate the absence of information about the apartment but these values don't ascertain the absence of such a feature in real life."

#Therefore the rows that contains 9 are dropped because it cannot be used even we take the average.

# Display the number of rows before dropping
print(f'Number of rows before dropping Full 9s: {len(df)}')

# Drop rows containing the specific value 9
def contains_exactly_9(x):
    if isinstance(x, int) or isinstance(x, float):
        return x == 9
    elif isinstance(x, str):
        # Split the string by spaces and check if '9' is an exact match in any part
        return '9' in x.split()
    return False

# Apply the function across the DataFrame and drop rows where any cell returns True
rows_to_drop = df.applymap(contains_exactly_9).any(axis=1)
df = df[~rows_to_drop]

# Display the number of rows after dropping
print(f'Number of rows after dropping Full 9s:: {len(df)}')


exclude_cols = ['Price', 'Area', 'Location', 'No. of Bedrooms']
# Convert all columns except the ones in exclude_cols to boolean type
df[df.columns.difference(exclude_cols)] = df[df.columns.difference(exclude_cols)].astype(bool)
df['Price'] = df['Price'].astype(int)
df['Area'] = df['Area'].astype(int)
df['No. of Bedrooms'] = df['No. of Bedrooms'].astype(int)
# Print a Series with the data type of each column
#print(df.dtypes)
df = df.drop(columns=['LiftAvailable'])

#Handling Incomplete Data 

# # Remove duplicates
df = df.drop_duplicates()

# Remove rows where the 'Price' is above 75 million
df = df[df['Price'] <= 75000000]

# Remove rows where the 'Area' is above 5000
df = df[df['Area'] <= 5000]

# Get the number of rows
num_rows = df.shape[0]
#print("Number of rows:", num_rows)

#Handling Typos / Data Consistency 
df = df.rename(columns={'No. of Bedrooms': 'NumOfBedrooms'})
df = df.rename(columns={"Children'splayarea": "ChildrenPlayArea"})
df = df.rename(columns={"Gasconnection": "GasConnection"})
df = df.rename(columns={"BED": "Bed"})
df = df.rename(columns={"ClubHouse": "Clubhouse"})

#Removing unused columns
df = df.drop(columns=['VaastuCompliant'])

# Providing a Surrogate Key for each row 
df['SurrogateKey'] = df.reset_index().index + 1


# Data Discretization: Converting 'Area' into discrete bins
df['Area Category'] = pd.cut(df['Area'], bins=3, labels=['Small', 'Medium', 'Large'])

# Feature Engineering: Creating a new feature, e.g., Price per square ft
df['Price per Square ft'] = df['Price'] / df['Area']

#Facts Table 

salesPriceDF = df[['Location', 'Area', 'Price']].reset_index()
salesPriceDF['SaleID'] = salesPriceDF.index + 1

#Creating the Dimension Tables  

householdApplianceDF = df[['WashingMachine', 'AC', 'Microwave', 'TV','Wardrobe','Refrigerator' ]]
outdoorAmentitiesDF = df[['SwimmingPool', 'LandscapedGardens', 'JoggingTrack', 'RainWaterHarvesting']]
communityDF = df[['ShoppingMall', 'SportsFacility', 'School','Hospital']]
indoorRoomsDF = df[['NumOfBedrooms', 'Gymnasium', 'IndoorGames','Clubhouse','MultipurposeRoom','ChildrenPlayArea']]

# householdApplianceDF['HouseHoldApplianceID'] = salesPriceDF['SaleID']
# outdoorAmentitiesDF['OutdoorAmentitieseID'] = salesPriceDF['SaleID']
# communityDF['CommunityID'] = salesPriceDF['SaleID']
# indoorRoomsDF['IndoorRoomID'] = salesPriceDF['SaleID']

householdApplianceDF['HouseHoldApplianceID'] = range(1, len(householdApplianceDF) + 1)
outdoorAmentitiesDF['OutdoorAmentitiesID'] = range(1, len(outdoorAmentitiesDF) + 1)
communityDF['CommunityID'] = range(1, len(communityDF) + 1)
indoorRoomsDF['IndoorRoomID'] = range(1, len(indoorRoomsDF) + 1)

salesPriceDF['HouseHoldApplianceID'] = householdApplianceDF['HouseHoldApplianceID']
salesPriceDF['OutdoorAmentitiesID'] = outdoorAmentitiesDF['OutdoorAmentitiesID']
salesPriceDF['CommunityID'] = communityDF['CommunityID']
salesPriceDF['IndoorRoomID'] = indoorRoomsDF['IndoorRoomID']



#Print rows after cleaning
print("After cleaning", len(df))

#For Visual Representation of the Data 
def plot_price_distribution(df):
    # Set the style of seaborn
    sns.set(style="whitegrid")

    # Create a figure and a grid of subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [0.2, 0.8]})

    # Formatter for millions
    millions_formatter = mticker.FuncFormatter(lambda x, _: f'{x/1_000_000:.1f}M')

    # Boxplot - for outliers
    sns.boxplot(x=df['Price'], ax=axs[0], color="violet")
    axs[0].set(xlabel='')
    # Applying currency formatting to the boxplot x-axis
    axs[0].xaxis.set_major_formatter(millions_formatter)

    # Histogram - for distribution
    sns.histplot(data=df, x='Price', ax=axs[1], kde=True, color="skyblue")
    # Applying currency formatting to the histogram x-axis
    axs[1].xaxis.set_major_formatter(millions_formatter)

    # Set titles and labels
    axs[0].set_title('Price Distribution and Outliers')
    axs[1].set_xlabel('Price')
    axs[1].set_ylabel('Frequency')

    plt.tight_layout()
    plt.show()

plot_price_distribution(df)

#For Visual Representation of the Data 
def plot_area_distribution(df):
    # Set the style of seaborn
    sns.set(style="whitegrid")

    # Create a figure and a grid of subplots
    fig, axs = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [0.2, 0.8]})

    # Boxplot - for outliers
    sns.boxplot(x=df['Area'], ax=axs[0], color="violet")
    axs[0].set(xlabel='')

    # Histogram - for distribution
    sns.histplot(data=df, x='Area', ax=axs[1], kde=True, color="skyblue")

    # Set titles and labels
    axs[0].set_title('Area Distribution and Outliers')
    axs[1].set_xlabel('Area')
    axs[1].set_ylabel('Frequency')

    plt.tight_layout()
    plt.show()

# Call the function with your DataFrame
plot_area_distribution(df)


# Create SQLAlchemy engine
engine = create_engine(connection_string)

# Send DataFrame to SQL database
# Replace 'table_name' with the name of the table you want to create or append to in your database
df.to_sql('originalframe', engine, if_exists='replace', index=False)
salesPriceDF.to_sql('salespricefactstable', engine, if_exists='replace', index=False)
householdApplianceDF.to_sql('householddimension', engine, if_exists='replace', index=False)
outdoorAmentitiesDF.to_sql('outdooramentitiesdimension', engine, if_exists='replace', index=False)
communityDF.to_sql('communitydimension', engine, if_exists='replace', index=False)
indoorRoomsDF.to_sql('indoorroomsdimension', engine, if_exists='replace', index=False)

# Select all rows from the 'standardDF' table and load into a DataFrame
salespricefactstable = pd.read_sql("SELECT * FROM salespricefactstable", engine)
householddimension = pd.read_sql("SELECT * FROM householddimension", engine)
outdooramentitiesdimension = pd.read_sql("SELECT * FROM outdooramentitiesdimension", engine)
communitydimension = pd.read_sql("SELECT * FROM communitydimension", engine)
indoorroomsdimension = pd.read_sql("SELECT * FROM indoorroomsdimension", engine)

print("First 10 Rows of Fact Table ")
print(salespricefactstable.head(10))
print("First 10 Rows of Household Dimension ")
print(householddimension.head(10))
print("First 10 Rows of Outdoor Amentities Dimension  ")
print(outdooramentitiesdimension.head(10))
print("First 10 Rows of Community Dimension ")
print(communitydimension.head(10))
print("First 10 Rows of Indoor Room Dimension")
print(indoorroomsdimension.head(10))

# Dispose of the engine
engine.dispose()

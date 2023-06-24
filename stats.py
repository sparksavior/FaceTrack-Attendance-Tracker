import pandas as pd
import matplotlib.pyplot as plt

# Load attendance record from CSV file
df = pd.read_csv('attendance.csv')

# Get total number of students detected
total_students = len(df['Name'].unique())

# Count number of known students present
known_present = len(df[df['Name'] != 'Unknown'])

# Count number of unknown students
unknown_present = len(df[df['Name'] == 'Unknown'])

# Display statistics
print(f'Total students detected: {total_students}')
print(f'Known students present: {known_present}')
print(f'Unknown students present: {unknown_present}')

# Plot a pie chart to visualize the statistics
labels = ['Known present', 'Unknown present']
sizes = [known_present, unknown_present]
colors = ['#008000', '#FF0000']
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
plt.axis('equal')
plt.title('Attendance Statistics')
plt.show()

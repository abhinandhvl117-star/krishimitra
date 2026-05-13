from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User

# auth
class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name  = forms.CharField(max_length=50, required=False)
    email      = forms.EmailField(required=True)
    city       = forms.CharField(
        max_length=100, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Palakkad, Thrissur, Kollam'}),
        help_text='Used to fetch local weather for your dashboard.'
    )
 
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'city')
 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.email      = self.cleaned_data['email']
        if commit:
            user.save()
        return user
 
 
class UpdateCityForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Palakkad, Mumbai, Bengaluru'})
    )
    
# forgot password 
class CustomPasswordResetForm(PasswordResetForm):
    """Uses email to find the user and send reset link."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter your registered email'})
    )
 
 
class CustomSetPasswordForm(SetPasswordForm):
    """Form for entering the new password after clicking reset link."""
    pass   

class OTPForm(forms.Form):

    otp = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter OTP',
            'class': 'form-input'
        })
    )
    
# crop form
class CropRecommendationForm(forms.Form):
    nitrogen = forms.FloatField(
        min_value=0, max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 90'})
    )
    phosphorus = forms.FloatField(
        min_value=0, max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 42'})
    )
    potassium = forms.FloatField(
        min_value=0, max_value=300,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 43'})
    )
    temperature = forms.FloatField(
        min_value=-10, max_value=60,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 28', 'step': '0.1'})
    )
    humidity = forms.FloatField(
        min_value=0, max_value=100,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 82', 'step': '0.1'})
    )
    ph = forms.FloatField(
        min_value=0, max_value=14,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 6.5', 'step': '0.1'})
    )
    rainfall = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 202', 'step': '0.1'})
    )
    
# disease form 
class DiseaseDetectionForm(forms.Form):
    image = forms.ImageField()
    
# price form
STATE_DISTRICTS = {
    'Punjab': ['Amritsar','Bhatinda','Faridkot','Fatehgarh','Fazilka','Ferozpur','Gurdaspur','Hoshiarpur','Jalandhar','Kapurthala','Ludhiana','Moga','Mohali','Muktsar','Patiala','Ropar (Rupnagar)','Sangrur','Tarntaran'],
    'Uttar Pradesh': ['Agra','Aligarh','Ambedkarnagar','Amroha','Auraiya','Ayodhya','Azamgarh','Badaun','Barabanki','Banda','Bareilly','Bijnor','Bulandshahar','Etah','Etawah','Farukhabad','Fatehpur','Gautam Budh Nagar','Ghaziabad','Ghazipur','Gonda','Gorakhpur','Hamirpur','Hardoi','Hathras','Jalaun (Orai)','Jhansi','Kasganj','Kanpur','Kanpur Dehat','Khiri (Lakhimpur)','Lakhimpur','Lalitpur','Lucknow','Mahoba','Maharajganj','Mainpuri','Mau(Maunathbhanjan)','Mirzapur','Muzaffarnagar','Pillibhit','Prayagraj','Pratapgarh','Raebarelli','Rampur','Saharanpur','Sambhal','Shahjahanpur','Shamli','Siddharth Nagar','Sitapur','Shravasti','Unnao'],
    'Madhya Pradesh': ['Alirajpur','Ashoknagar','Badwani','Balaghat','Betul','Bhind','Bhopal','Burhanpur','Chhatarpur','Chhindwara','Damoh','Datia','Dewas','Dhar','Dindori','Guna','Gwalior','Harda','Hoshangabad','Indore','Jabalpur','Jhabua','Katni','Khandwa','Khargone','Mandla','Mandsaur','Morena','Narsinghpur','Neemuch','Panna','Raisen','Rajgarh','Ratlam','Rewa','Sagar','Satna','Sehore','Seoni','Shajapur','Sheopur','Shivpuri','Tikamgarh','Ujjain','Umariya','Vidisha'],
    'Rajasthan': ['Alwar','Baran','Barmer','Bharatpur','Beawar','Bikaner','Bundi','Chittorgarh','Churu','Dausa','Deeg','Dholpur','Dungarpur','Ganganagar','Hanumangarh','Jaipur','Jaisalmer','Jalore','Jhalawar','Jhunjhunu','Kota','Pratapgarh','Sikar','Swai Madhopur','Tonk','Udaipur'],
    'Chattisgarh': ['Dantewada','Durg','Jashpur','Kanker','Koria','Mahasamund','Rajnandgaon','Surajpur'],
    'Assam': ['Kamrup'],
    'West Bengal': ['Darjeeling','Dakshin Dinajpur','Hooghly','Howrah','Jhargram','Kolkata','Malda','Medinipur(E)','Medinipur(W)','Murshidabad','Nadia','North 24 Parganas','Purba Bardhaman','Puruliya','Sounth 24 Parganas'],
    'Haryana': ['Ambala','Fatehabad','Gurgaon','Hissar','Jhajar','Jind','Kaithal','Kurukshetra','Mahendragarh-Narnaul','Mewat','Panchkula','Panipat','Rewari','Rohtak','Sirsa','Sonipat','Yamuna Nagar'],
    'Gujarat': ['Ahmedabad','Amreli','Anand','Banaskanth','Bharuch','Bhavnagar','Botad','Chhota Udaipur','Dahod','Devbhumi Dwarka','Gandhinagar','Gir Somnath','Jamnagar','Junagarh','Kachchh','Kheda','Mehsana','Morbi','Narmada','Navsari','Panchmahals','Patan','Porbandar','Rajkot','Sabarkantha','Surat','Surendranagar','Vadodara(Baroda)','Valsad'],
    'NCT of Delhi': ['Delhi'],
    'Maharashtra': ['Ahmednagar','Jalana','Jalgaon','Kolhapur','Nagpur','Nashik','Pune','Raigad','Sangli','Satara','Thane'],
    'Tripura': ['Dhalai','North Tripura','Unokoti'],
    'Kerala': ['Alappuzha','Ernakulam','Idukki','Kannur','Kasargod','Kollam','Kottayam','Kozhikode(Calicut)','Malappuram','Palakad','Pathanamthitta','Thiruvananthapuram','Thirssur','Wayanad'],
    'Himachal Pradesh': ['Bilaspur','Chamba','Hamirpur','Kangra','Kullu','Mandi','Sirmore','Solan','Una'],
    'Karnataka': ['Bangalore','Belgaum','Chamrajnagar','Chitradurga','Davangere','Haveri','Karwar(Uttar Kannad)','Kolar','Koppal','Madikeri(Kodagu)','Mysore','Raichur','Shimoga','Tumkur'],
    'Telangana': ['Adilabad','Bhadradri Kothagudem','Hyderabad','Jagityal','Karimnagar','Khammam','Mahbubnagar','Medak','Nalgonda','Ranga Reddy','Warangal'],
    'Odisha': ['Balasore','Bargarh','Bhadrak','Bolangir','Boudh','Cuttack','Dhenkanal','Jagatsinghpur','Jajpur','Jharsuguda','Kalahandi','Kendrapara','Keonjhar','Khurda','Koraput','Mayurbhanja','Nayagarh','Nuapada','Rayagada','Sambalpur','Sonepur','Sundergarh'],
    'Andhra Pradesh': ['Annamayya','Chittor','East Godavari','Guntur','Kurnool','Nellore','Palnadu','Visakhapatnam','West Godavari'],
    'Uttarakhand': ['Dehradoon','Garhwal (Pauri)','Haridwar','Nanital','Udhamsinghnagar'],
    'Goa': ['North Goa'],
    'Nagaland': ['Dimapur','Kohima'],
    'Jammu and Kashmir': ['Jammu','Kathua'],
    'Andaman and Nicobar': ['North and Middle Andaman'],
    'Chandigarh': ['Chandigarh'],
    'Meghalaya': ['East Khasi Hills'],
    'Arunachal Pradesh': ['Lower Subansiri'],
}
 
STATE_CHOICES = [(s, s) for s in sorted(STATE_DISTRICTS.keys())]

DISTRICT_CHOICES = [(d, d) for state_districts in STATE_DISTRICTS.values() for d in state_districts]

COMMODITY_CHOICES = [
    ('Ajwan', 'Ajwan'),
    ('Amaranthus', 'Amaranthus'),
    ('Apple', 'Apple'),
    ('Arecanut(Betelnut/Supari)', 'Arecanut(Betelnut/Supari)'),
    ('Ashgourd', 'Ashgourd'),
    ('Asgand', 'Asgand'),
    ('Banana', 'Banana'),
    ('Banana - Green', 'Banana - Green'),
    ('Barley(Jau)', 'Barley(Jau)'),
    ('Beans', 'Beans'),
    ('Beaten Rice', 'Beaten Rice'),
    ('Beetroot', 'Beetroot'),
    ('Bengal Gram(Gram)(Whole)', 'Bengal Gram(Gram)(Whole)'),
    ('Bhindi(Ladies Finger)', 'Bhindi(Ladies Finger)'),
    ('Bitter gourd', 'Bitter gourd'),
    ('Black pepper', 'Black pepper'),
    ('Black Gram(Urd Beans)(Whole)', 'Black Gram(Urd Beans)(Whole)'),
    ('BOP', 'BOP'),
    ('Bottle gourd', 'Bottle gourd'),
    ('Brinjal', 'Brinjal'),
    ('Cabbage', 'Cabbage'),
    ('Capsicum', 'Capsicum'),
    ('Carrot', 'Carrot'),
    ('Castor Seed', 'Castor Seed'),
    ('Cauliflower', 'Cauliflower'),
    ('Chikoos(Sapota)', 'Chikoos(Sapota)'),
    ('Chili Red', 'Chili Red'),
    ('Chilly Capsicum', 'Chilly Capsicum'),
    ('Chrysanthemum', 'Chrysanthemum'),
    ('Cluster beans', 'Cluster beans'),
    ('Coconut', 'Coconut'),
    ('Coffee', 'Coffee'),
    ('Copra', 'Copra'),
    ('Coriander(Leaves)', 'Coriander(Leaves)'),
    ('Corriander seed', 'Corriander seed'),
    ('Cotton', 'Cotton'),
    ('Cow', 'Cow'),
    ('Cowpea(Lobia/Karamani)', 'Cowpea(Lobia/Karamani)'),
    ('Cowpea(Veg)', 'Cowpea(Veg)'),
    ('Cucumbar(Kheera)', 'Cucumbar(Kheera)'),
    ('Cummin Seed(Jeera)', 'Cummin Seed(Jeera)'),
    ('Dhaincha', 'Dhaincha'),
    ('Drumstick', 'Drumstick'),
    ('Dry Chillies', 'Dry Chillies'),
    ('Field Pea', 'Field Pea'),
    ('Firewood', 'Firewood'),
    ('Fish', 'Fish'),
    ('Foxtail Millet(Navane)', 'Foxtail Millet(Navane)'),
    ('French Beans(Frasbean)', 'French Beans(Frasbean)'),
    ('Garlic', 'Garlic'),
    ('Ginger(Dry)', 'Ginger(Dry)'),
    ('Ginger(Green)', 'Ginger(Green)'),
    ('Goat', 'Goat'),
    ('Grapes', 'Grapes'),
    ('Green Chilli', 'Green Chilli'),
    ('Green Gram(Moong)(Whole)', 'Green Gram(Moong)(Whole)'),
    ('Green Peas', 'Green Peas'),
    ('Groundnut', 'Groundnut'),
    ('Guar', 'Guar'),
    ('Guava', 'Guava'),
    ('Gur(Jaggery)', 'Gur(Jaggery)'),
    ('Indian Beans(Seam)', 'Indian Beans(Seam)'),
    ('Jack Fruit(Ripe)', 'Jack Fruit(Ripe)'),
    ('Jowar(Sorghum)', 'Jowar(Sorghum)'),
    ('Kabuli Chana(Chickpeas-White)', 'Kabuli Chana(Chickpeas-White)'),
    ('Knool Khol', 'Knool Khol'),
    ('Lemon', 'Lemon'),
    ('Lentil(Masur)(Whole)', 'Lentil(Masur)(Whole)'),
    ('Lime', 'Lime'),
    ('Maize', 'Maize'),
    ('Mango', 'Mango'),
    ('Mango(Raw-Ripe)', 'Mango(Raw-Ripe)'),
    ('Methi Seeds', 'Methi Seeds'),
    ('Mustard', 'Mustard'),
    ('Onion', 'Onion'),
    ('Orange', 'Orange'),
    ('Papaya', 'Papaya'),
    ('Peas Wet', 'Peas Wet'),
    ('Pineapple', 'Pineapple'),
    ('Pointed gourd(Parval)', 'Pointed gourd(Parval)'),
    ('Pomegranate', 'Pomegranate'),
    ('Potato', 'Potato'),
    ('Pumpkin', 'Pumpkin'),
    ('Raddish', 'Raddish'),
    ('Rice', 'Rice'),
    ('Rubber', 'Rubber'),
    ('Snakeguard', 'Snakeguard'),
    ('Soyabean', 'Soyabean'),
    ('Spinach', 'Spinach'),
    ('Sugar', 'Sugar'),
    ('Sweet Potato', 'Sweet Potato'),
    ('Tamarind Fruit', 'Tamarind Fruit'),
    ('Tapioca', 'Tapioca'),
    ('Tender Coconut', 'Tender Coconut'),
    ('Tomato', 'Tomato'),
    ('Turmeric(raw)', 'Turmeric(raw)'),
    ('Water Melon', 'Water Melon'),
    ('Wheat', 'Wheat'),
    ('Wheat Atta', 'Wheat Atta'),
    ('Yam', 'Yam'),
]

class PricePredictionForm(forms.Form):
    state     = forms.ChoiceField(choices=STATE_CHOICES)
    district  = forms.CharField(max_length=100)   
    commodity = forms.ChoiceField(choices=COMMODITY_CHOICES)
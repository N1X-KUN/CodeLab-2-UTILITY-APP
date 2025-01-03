from PIL import Image, ImageTk
from io import BytesIO
import requests
import pygame
import tkinter as tk

# Initialize pygame for music playback
pygame.mixer.init()
pygame.mixer.music.load("PokemonBGM.mp3")
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1, 0.0)  # Loop music indefinitely

is_muted = False

def get_pokemon_info(identifier):
    # Fetch Pokémon data from the API
    url = f"https://pokeapi.co/api/v2/pokemon/{identifier}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()  # Return JSON data if successful
    else:
        return None  # Return None if Pokémon not found

def update_ui(data):
    if data:
        # Update the displayed Pokémon details
        name_id_text.set(f"{data['name'].capitalize()} (ID: {data['id']})")
        type_text.set(", ".join([t["type"]["name"].capitalize() for t in data["types"]]))
        species_text.set(data["species"]["name"].capitalize())
        abilities_text.set(", ".join([a["ability"]["name"].capitalize() for a in data["abilities"]]))
        stats = "\n".join([f"{stat['stat']['name'].capitalize()}: {stat['base_stat']}" for stat in data.get('stats', [])])
        stats_text.set(f"{stats}")

        # Fetch and display description
        species_url = data["species"]["url"]
        species_response = requests.get(species_url)
        if species_response.status_code == 200:
            species_data = species_response.json()
            flavor_text_entries = species_data.get("flavor_text_entries", [])
            flavor_text = next((entry["flavor_text"] for entry in flavor_text_entries if entry["language"]["name"] == "en"), "Description not available.")
            details_text.set(flavor_text)
            weight_height_text.set(f"Weight: {data['weight'] / 10.0} kg\nHeight: {data['height'] / 10.0} m")
        else:
            # Fallback for missing species data
            details_text.set("Description not available.")
            weight_height_text.set(f"Weight: {data['weight'] / 10.0} kg\nHeight: {data['height'] / 10.0} m")

        # Display Pokémon image
        image_url = data['sprites']['other']['official-artwork']['front_default']
        if image_url:
            response = requests.get(image_url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            pokemon_image_label.config(image=photo, bg="black")
            pokemon_image_label.image = photo
        else:
            # Reset image if none available
            pokemon_image_label.config(image="", bg="black")
            pokemon_image_label.image = None

    else:
        # Handle invalid Pokémon input
        name_id_text.set("THE POKEDEX")
        type_text.set("HAVE NEVER")
        species_text.set("DISCOVERED THAT")
        abilities_text.set("POKEMON DATA")
        stats_text.set("No Stats Available")
        details_text.set("No Available Description")
        weight_height_text.set("Unknown Weight and Height")

        # Fallback image for invalid Pokémon
        fallback_image_url = "https://i.imgflip.com/73qk92.jpg"
        response = requests.get(fallback_image_url)
        if response.status_code == 200:
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            img = img.resize((200, 200))
            fallback_photo = ImageTk.PhotoImage(img)
            pokemon_image_label.config(image=fallback_photo, bg="red")
            pokemon_image_label.image = fallback_photo
        else:
            # Red box with no image as final fallback
            pokemon_image_label.config(image="", bg="red")
            pokemon_image_label.image = None

def select_pokemon(move=None):
    # Handle Pokémon navigation or search
    global current_pokemon_id
    if move == "forward":
        if current_pokemon_id is not None:
            current_pokemon_id += 1
    elif move == "backward" and current_pokemon_id and current_pokemon_id > 1:
        current_pokemon_id -= 1
    else:
        # Handle user input for search
        user_input = search_entry.get().strip().lower()
        if user_input.isdigit():
            current_pokemon_id = int(user_input)
        else:
            data = get_pokemon_info(user_input)
            if data:
                current_pokemon_id = data.get('id', None)
            else:
                current_pokemon_id = None
                update_ui(None)
                return
    # Update UI with fetched data
    if current_pokemon_id:
        data = get_pokemon_info(current_pokemon_id)
        update_ui(data)

def toggle_mute():
    # Toggle music mute state
    global is_muted
    if is_muted:
        pygame.mixer.music.set_volume(0.5)
        music_button.config(image=music_icon)
    else:
        pygame.mixer.music.set_volume(0)
        music_button.config(image=unmute_icon)
    is_muted = not is_muted

# Tkinter GUI setup
root = tk.Tk()
root.title("Pokédex")
root.geometry("500x700")
root.configure(bg="red")
icon_img = tk.PhotoImage(file="PokIcon.png")  
root.iconphoto(False, icon_img)

current_pokemon_id = 1  # Initialize starting Pokémon ID
name_id_text = tk.StringVar(value="Name and ID")
type_text = tk.StringVar(value="Type/Element")
species_text = tk.StringVar(value="Species")
abilities_text = tk.StringVar(value="Abilities")
stats_text = tk.StringVar(value="Pokémon Stats")
details_text = tk.StringVar(value="Pokémon Description")

# Logo and header
header_frame = tk.Frame(root, bg="red")
header_frame.grid(row=0, column=0, columnspan=2, pady=10)
header_label = tk.Label(header_frame, text="POKÉDEX", font=("Fixedsys", 24), bg="red", fg="white")
header_label.pack(side=tk.LEFT, padx=5)

# Image handling
logo_url = "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj-1s83_Kcbpm3txAxOt2Jrq3GgjdM5EUOhZB-zfuohbf-wCgBo5NY-6pxc6Cd-zq8103xGStty7QY0390i2bBsPmO31-Or8YbtoXjBamuHBDzelL7QOUIvdLqZgk92PdeiZD_1fEO3UAU/s1600/Pok%C3%A9Battle+Logo.png"
response = requests.get(logo_url)
logo_img_data = response.content
logo_img = Image.open(BytesIO(logo_img_data))
logo_img = logo_img.resize((50, 50))
logo_photo = ImageTk.PhotoImage(logo_img)

logo_label = tk.Label(header_frame, image=logo_photo, bg="red")
logo_label.image = logo_photo
logo_label.pack(side=tk.LEFT, padx=5)

# Frame for search functionality
search_frame = tk.Frame(header_frame)
search_frame.pack(side=tk.LEFT, padx=5)
search_entry = tk.Entry(search_frame, font=("Fixedsys", 16), width=20)
search_entry.pack(side=tk.LEFT)
tk.Button(search_frame, text="Search", font=("Fixedsys", 16), command=lambda: select_pokemon()).pack(side=tk.LEFT)

# Frame for displaying Pokemon details
details_frame = tk.Frame(root, bg="red")
details_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# Label to display Pokemon image
pokemon_image_label = tk.Label(root, bg="black", width=200, height=200)
pokemon_image_label.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

# Labels for various Pokemon details
tk.Label(details_frame, textvariable=name_id_text, font=("Fixedsys", 12), bg="light blue", fg="black", anchor="center", wraplength=250).grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
tk.Label(details_frame, textvariable=type_text, font=("Fixedsys", 12), bg="light blue", fg="black", anchor="center", wraplength=250).grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
tk.Label(details_frame, textvariable=species_text, font=("Fixedsys", 12), bg="light blue", fg="black", anchor="center", wraplength=250).grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
tk.Label(details_frame, textvariable=abilities_text, font=("Fixedsys", 12), bg="light blue", fg="black", anchor="center", wraplength=250).grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

# Configure grid layout for details_frame
details_frame.grid_rowconfigure(0, weight=1)
details_frame.grid_rowconfigure(1, weight=1)
details_frame.grid_rowconfigure(2, weight=1)
details_frame.grid_rowconfigure(3, weight=1)
details_frame.grid_columnconfigure(0, weight=1)

# Frame for Pokemon stats
stats_frame = tk.Frame(root, bg="red")
stats_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

# Frame for additional details text
details_text_frame = tk.Frame(root, bg="red")
details_text_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

# Label for displaying stats
tk.Label(stats_frame, textvariable=stats_text, font=("Fixedsys", 16), bg="white", fg="black", anchor="center", justify="center", wraplength=250).grid(row=0, column=0, sticky="nsew", pady=5)

# Label for description
tk.Label(details_text_frame, text="Description", font=("Fixedsys", 16), bg="white", fg="black").grid(row=0, column=0, sticky="nsew", pady=5)
tk.Label(details_text_frame, textvariable=details_text, font=("Fixedsys", 16), bg="white", fg="black", justify="center", wraplength=250).grid(row=0, column=0, sticky="nsew", pady=5)

# Label for weight and height
weight_height_text = tk.StringVar(value="Weight: N/A\nHeight: N/A")
tk.Label(details_text_frame, textvariable=weight_height_text, font=("Fixedsys", 16), bg="white", fg="black", justify="center", wraplength=250).grid(row=1, column=0, sticky="nsew", pady=5)

# Configure grid layout for frames
stats_frame.grid_rowconfigure(0, weight=1)
stats_frame.grid_columnconfigure(0, weight=1)
details_text_frame.grid_rowconfigure(0, weight=1)
details_text_frame.grid_columnconfigure(0, weight=1)

# Frame for footer with navigation buttons and music control
footer_frame = tk.Frame(root, bg="red")
footer_frame.grid(row=3, column=0, columnspan=2, pady=10)

# 'Back' button
left_button = tk.Button(footer_frame, text="Back", font=("Fixedsys", 16), command=lambda: select_pokemon("backward"))
left_button.grid(row=0, column=0, padx=5)

# Music icon and button
music_icon_url = "https://m.media-amazon.com/images/I/61FEgQfZc8L.png"
music_img = Image.open(requests.get(music_icon_url, stream=True).raw)
music_img = music_img.resize((30, 30), Image.Resampling.LANCZOS)
music_icon = ImageTk.PhotoImage(music_img)
unmute_icon_url = "https://m.media-amazon.com/images/I/61FEgQfZc8L.png"
unmute_img = Image.open(requests.get(unmute_icon_url, stream=True).raw)
unmute_img = unmute_img.resize((30, 30), Image.Resampling.LANCZOS)
unmute_icon = ImageTk.PhotoImage(unmute_img)

# Music button with icon
music_button = tk.Button(footer_frame, image=music_icon, command=toggle_mute, bg="red", borderwidth=0)
music_button.grid(row=0, column=1, padx=5)

# 'Next' button
right_button = tk.Button(footer_frame, text="Next", font=("Fixedsys", 16), command=lambda: select_pokemon("forward"))
right_button.grid(row=0, column=2, padx=5)

# Fetch and update UI with Pokemon info
data = get_pokemon_info("bulbasaur")
update_ui(data)

# Configure root window layout
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Final grid configuration for details_frame
details_frame.grid_rowconfigure(0, weight=1)
details_frame.grid_rowconfigure(1, weight=1)
details_frame.grid_rowconfigure(2, weight=1)
details_frame.grid_rowconfigure(3, weight=1)
details_frame.grid_columnconfigure(0, weight=1)

root.mainloop()
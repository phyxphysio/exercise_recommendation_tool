import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import webbrowser

# Store data
df = pd.read_csv("phyx_exs_data.csv")
df['Body Part'] = [' '.join(part.split('-')).capitalize() for part in df['Body Part']]

# Create string with exercise qualities that allows u to compare
def combine_qualities(data):
    return [
        data["Difficulty"][i] + " " + data["Body Part"][i] + " " + data["Equipment"][i]
        for i in range(data.shape[0])
    ]


# Create a column to hold combined qualities
df["combined_qualities"] = combine_qualities(df)

# Convert combined qualities string into token matrix
cm = CountVectorizer().fit_transform(df["combined_qualities"])

# Get cosine similarity from token matrix
cs = cosine_similarity(cm)

# Add exercise id to df
df["exs_id"] = list(range(df.shape[0]))


# Introduce the program an choose recommendation method
def intro():
    print("Welcome to the Phyx Exercise Prescription Algorithm! \n")
    recommendation_method = None
    while recommendation_method not in ["1", "2"]:
        recommendation_method = input(
            "You can receive recommendations based on:\n1 An exercise you like\n2 The part of the body you'd like to work\nType the number of the option you'd like to select: "
        )
        if recommendation_method not in ["1", "2"]:
            print(f"\n'{recommendation_method}' isn't an option. Type '1' or '2'\n")
    if recommendation_method == "1":
        print_score()
        try_again()
    elif recommendation_method == "2":
        display_exercises_in_region(get_body_part())


# Get exercise from user
def get_input():
    print(df.Name.to_string())
    exs_id = int(input("Type the number of the exercise to see similar ones:"))
    while exs_id not in range(df.shape[0]):
        print("That's not a valid option. Try again.")
        get_input()
    return exs_id


# Compare and display top matches
def print_score():
    exs_id = get_input()

    # Create enumerated list of similar exercises
    scores = list(enumerate(cs[exs_id]))

    # Sort the list of scores
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # Remove base exercise from list of matches
    for i in sorted_scores:
        if i[0] == exs_id:
            sorted_scores.remove(i)

    exs_name = df[df.exs_id == exs_id]["Name"].values[0]
    print(f"The closest exercises to the {exs_name} are: \n")
    j = 0
    for i in sorted_scores:
        rec_name = df[df.exs_id == i[0]]["Name"].values[0]
        rec_score = str(int(i[1] * 100)) + "%"
        print(j + 1, rec_name, rec_score)
        j += 1
        if j > 5:
            break


# Allow the user ot keep comparing
def try_again():
    ask = input("Want to go again? Type 'y' or 'n'")
    if ask == "y":
        intro()
    elif ask == "n":
        see_videos()
    else:
        print("Enter a valid input (y or n):")
        try_again()


# Add recommendation by category functionality
body_part_column = df["Body Part"]


# Create list of body parts for user to chose from
def listify_strings(column):
    return [i.split(",") for i in column]


df["regions_listed"] = listify_strings(body_part_column)


def compile_part_list(column):
    part_list = []
    cleaned_regions_list = []
    for i in range(len(column)):
        cleaned_regions_list.append([])
        for region in column[i]:
            region = region.replace(" ", "")
            region = region.title()
            cleaned_regions_list[i].append(region)
            if region not in part_list:
                part_list.append(region)
            else:
                continue

    return part_list, cleaned_regions_list


body_part_list = compile_part_list(df["regions_listed"])[0]
cleaned_regions_column = compile_part_list(df["regions_listed"])[1]


# Use autocomplete to help user choose category
def get_first_letter():
    return input(
        "\nWhich body part would you like to work?\nType the first letter to see the corresponding options.\n"
    )


def get_body_part():
    first_letter_of_category = get_first_letter().lower()
    j = -1
    region_with_first_letter = []
    for region in body_part_list:
        if region[0].lower() == first_letter_of_category:
            j += 1
            region_with_first_letter.append(region)
            print(j, region)

    # If the user does not enter a valid letter, prompt adan with a list of options
    if j < 0:
        print(
            f"\nWe couldn't find any categories starting with '{first_letter_of_category}'.\nHere's a list of the categories have:\n"
        )
        for region in body_part_list:
            j += 1
            print(j, region)
            region_with_first_letter.append(region)

    # Allow the user to choose from the subset they hve chosen

    region_choice = None
    while region_choice not in range(len(region_with_first_letter)):
        try:
            region_choice = int(
                input("Type the number of the body part you'd like t work.")
            )
        except ValueError:
            print("Type a number.")
    return region_with_first_letter[int(region_choice)]


# Display the exercises in the category chosen by the user
def display_exercises_in_region(region):
    rows_to_keep = [
        i
        for i in range(len(cleaned_regions_column))
        if region in cleaned_regions_column[i]
    ]
    exs_to_display = df.drop([i for i in range(df.shape[0]) if i not in rows_to_keep])
    exs_to_display = exs_to_display.drop(
        ["exs_id", "regions_listed", "combined_qualities", "Body Part"], axis=1
    )
    print(f"Here are the exercises that work the {region}.\n")
    print(exs_to_display)
    try_again()


# Allow user to open exercise video on youtube
def see_videos():
    choice = None
    while choice not in ["y", "n"]:
        choice = input(
            "\nWould you lke to see videos of these exercises in your web browser?\nType 'y' or 'n' to select: "
        )
        if choice not in ["y", "n"]:
            print(f"\n{choice} isn't an option.")
    if choice == "y":
        webbrowser.open(
            "https://www.youtube.com/playlist?list=PLpqyTnl8cO1m3kL5goWP45PKkz1QfxRwF"
        )
    if choice == "n":
        print("Okay, see ya next time!")


intro()

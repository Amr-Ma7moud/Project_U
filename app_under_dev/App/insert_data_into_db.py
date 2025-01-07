from sqlite3 import IntegrityError
from App.models import University
from App import db
import csv

def insert_universities_from_csv(file_path):
    with open(file_path, mode="r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                university = University(
                    name=row["name"],
                    website=row["website"],
                    university_type=row["type"],
                    location=row["location"],
                    rank=int(
                        row["rank"]
                    ),  # rank parsed correctly as int using local methods for this
                    fees=int(
                        row["fees"]
                    ),  # type casting added, if data exists that follows that
                    description=row.get("description", ""),
                    programs=row["programs"],
                    min_score=int(
                        row["min_score"]
                    ),  # parsed to integers , before value is passed
                    world_ranking=int(
                        row["world_ranking"]
                    ),  # world ranking integer, add check before insert from python to validation format . before table data entry, same method can extended other types of input check that needs be done on user end or form field . UI method use that same techniques too . for "format based  data input check
                    abbreviations=row[
                        "abbreviations"
                    ],  # unique string that mostly used  UI or view tag  properties / attributes values for dom handling and/ or also UI framework local implementations. these local ids are unique as HTML id also be that specific strings by their html component names
                )
                db.session.add(university)
                db.session.commit()
                print(f"Added university: {row['name']}")
            except IntegrityError:
                db.session.rollback()
                print(f"Skipping duplicate entry: {row['name']}")
            except (
                ValueError
            ) as ve:  # catches specific type of parsing/ cast method errors for all number format values at server/ db level operations that has invalid numerical strings
                print(
                    f"Error parsing data , number / type problem found for {row['name']},and skip  due to  Error: {ve}, try updating data on CSV using integer range etc , check string types that you intended  / value validations at server db before save methods are applied! "
                )

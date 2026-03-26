import discord
from discord.ext import commands
from discord import app_commands
import random
import re
import hundredNPCTable as NPCTables
import tokenDeposit

# Discord Client class.
class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')



#Table Roller. Administers all the table rolling and result process.
class TableRoller:
    def __init__(self, tables= None):
        self.tables = tables if tables else NPCTables.TABLES_INDEX
        
        #Picks a random option in a specific table
    def roll_table(self,table):
        return random.choice(table)
        
        #Generate table rolls. It's the main method.
    def generate(self,category):
        result = {}
        if category not in self.tables:
            result = {"Invalid Table. Please check writing and try again."}
        else:
            for name, table in self.tables[category].items():
                roll = self.roll_table(table)
                roll = self.resolve(roll,category)
                result[name] = roll
            result = self.format(result)
        return result
        
        #Roll in the auxiliary tables if the option has "See Table: X" and replaces the text with the result from Table X.
    def resolve(self, text,category):
        pattern = r"\(See Table: (.*?)\)"
        matches = re.findall(pattern, text)
        
        for match in matches:
            if match in self.tables:
                subResult = self.generate(match)
                if isinstance(subResult, dict):
                    replacement = ", ".join(subResult.values())
                else:
                    replacement = match + '\n' + str(subResult)
                text = text.replace(f"(See Table: {match})", replacement)
        return text
    
    #Formats the resulting string and adds line breaks
    def format(self, result):
        if isinstance(result,dict):
            return "\n".join(f"{key}: {value}" for key, value in result.items())   
        return str(result)
    
    #Returns the name of all avaliable tables.
    def get_categories_text(self):
        return "\n".join(self.tables.keys())
        

intents = discord.Intents.default()
intents.message_content = True
roller = TableRoller()
client = Client(command_prefix="!", intents= intents)
discordToken = tokenDeposit.discordToken

#'Slash' commands

#Slash command to roll details of an entire character
@client.tree.command(name="rollcharacter", description="rolls a brand new random character")
async def createCharacter(interaction: discord.Interaction):
    embed = discord.Embed(title="ALEA IACTA EST. The die has been cast.", description=f'Here is the details of your character:', color= discord.Colour.green())
    embed.add_field(name="FLAW", value=roller.generate("Flaws"))
    embed.add_field(name="STRUGGLES", value=roller.generate("Struggles"))
    embed.add_field(name="PROP", value=roller.generate("Prop"))
    embed.add_field(name="WORLD CONNECTION", value=roller.generate("Connection"))
    embed.add_field(name="ATTRIBUTES", value=roller.generate("Attributes"))
    embed.add_field(name="STORY HOOK", value=roller.generate("Hooks"))
    await interaction.response.send_message(embed=embed, ephemeral=True)

#Slash command to roll from a specific table.
@client.tree.command(name="rolltable", description="select table to roll")
async def selectTable(interaction: discord.Interaction, text:str):
    embed = discord.Embed(title="ALEA IACTA EST. The die has been cast.", description=f'Chosen table: {text}', color= discord.Colour.purple())
    embed.add_field(name="Result", value=roller.generate(text))
    await interaction.response.send_message(embed=embed, ephemeral=True)

#Slash command to show all tables avaliable.
@client.tree.command(name="showtables", description="Show all avaliable tables")
async def showTables(interaction: discord.Interaction):
    text = roller.get_categories_text()
    await interaction.response.send_message(f"{interaction.user.mention}, those are the name of tables avaliable: \n" + text, ephemeral=True)

#Slash command to send instructions on using the bot.
@client.tree.command(name="rollhelp", description="Explain the bot to you.")
async def showHelp(interaction: discord.Interaction):
    await interaction.response.send_message(f"{interaction.user.mention}\n You can use the following commands: \n /rollcharacter. It will roll basic details for a character. \n /showtables. Will list the avaliable tables and their names.\n /rolltables. Roll on the table that you specify. \n WARNING: Will need to write the name of the table EXACTLY as shown by the /showtables command.\n Don't forget to print or copy the results you like for later use.", ephemeral=True)

# YOU NEED TO INSERT A DISCORD BOT TOKEN HERE FOR IT TO WORK. Enable all chat permissions.
client.run(discordToken)




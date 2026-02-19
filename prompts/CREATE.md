# General Guidelines

{{ system_prompt }}

# Task

Write a plan for a 4 1-hour session campaign for 4 party members. Produce the following notes under campaigns/<campaign-name>:

- campaigns/<campaign-name>/summary: High level summary of what will happen in this campaign. Delineate which events happen in each session. Consider choices that the characters can make during the campaign and plan for contingencies
- campaigns/<campaign-name>/session1/plan: A prompt to the dungeon master model on how to run the first session. 

Note that the DM model will start with only the context provided in the summary and session plan. It will also have access to any notes you write. Please write additional detailed notes for any significant npc / monster, place, or item. It may be useful to include any specific rules associated with these things (for example, writing out proper stat blocks for npcs and monsters).

Here's a directory structure you can use:
- campaigns/<campaign-name>/nps
- campaigns/<campaign-name>/monsters
- campaigns/<campaign-name>/places
- campaigns/<campaign-name>/items


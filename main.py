from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup from telegram.ext import ( ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, filters ) from datetime import datetime, timedelta import json import os

BOT_TOKEN = "8182668242:AAGpy6WMoYVJ5y_OLKd4FKWSFjixxggmHxY" CREATOR_USERNAME = "Reku_Senpai" DATA_FILE = "crossover.json"

crossover_data = {} user_status = {} CHOOSING_NAME, CHOOSING_DURATION, CHOOSING_INTRO, CHOOSING_OBJECTIVE, CHOOSING_PHOTO = range(5) MODIFY_SELECT, MODIFY_INPUT = range(5, 7)

def save_data(): with open(DATA_FILE, "w") as f: json.dump({"crossover": crossover_data, "users": user_status}, f)

def load_data(): if os.path.exists(DATA_FILE): with open(DATA_FILE, "r") as f: try: data = json.load(f) crossover_data.update(data.get("crossover", {})) user_status.update(data.get("users", {})) except Exception as e: print("Erreur chargement:", e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("👋 Bienvenue ! Tape /crossover pour voir le crossover en cours.")

async def crossover_command(update: Update, context: ContextTypes.DEFAULT_TYPE): if not crossover_data: await update.message.reply_text("⚠️ Aucun crossover actif.") return

username = update.message.from_user.username or f"id_{update.message.from_user.id}"
status = user_status.get(username, {})
seen = status.get("seen", False)
joined = status.get("status") == "joined"

msg = (
    f"🎭 *{crossover_data['name']}*\n\n"
    f"📝 {crossover_data['intro']}\n\n"
    f"🎯 *Objectif* : {crossover_data['objective']}\n"
    f"⏳ *Durée* : {crossover_data['duration']} jours\n"
    f"📅 *Fin* : {crossover_data['end']}"
)

if not seen:
    keyboard = [
        [InlineKeyboardButton("✅ Rejoindre", callback_data="join")],
        [InlineKeyboardButton("❌ Ignorer", callback_data="ignore")],
        [InlineKeyboardButton("🗑 Fermer", callback_data="close")]
    ]
else:
    keyboard = [[InlineKeyboardButton("🗑 Fermer", callback_data="close")]]
await context.bot.send_photo(
    chat_id=update.effective_chat.id,
    photo=crossover_data["photo"],
    caption=msg,
    parse_mode="Markdown",
    reply_markup=InlineKeyboardMarkup(keyboard)
)

async def handle_join(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query username = query.from_user.username or f"id_{query.from_user.id}" user_status[username] = {"status": "joined", "seen": True} save_data() await query.message.delete() await query.message.chat.send_message("✅ Tu as rejoint le crossover !") await query.answer()

async def handle_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE): query = update.callback_query username = query.from_user.username or f"id_{query.from_user.id}" user_status[username] = {"status": "ignored", "seen": True} save_data() await query.message.delete() await query.message.chat.send_message("🚫 Tu as ignoré le crossover.") await query.answer()

async def handle_close(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.callback_query.message.delete() await update.callback_query.answer()

async def participants_command(update: Update, context: ContextTypes.DEFAULT_TYPE): joined = [f"@{u}" for u, v in user_status.items() if v.get("status") == "joined"] if not joined: await update.message.reply_text("👥 Aucun participant pour l’instant.") else: await update.message.reply_text("👥 Participants :\n" + "\n".join(joined), parse_mode="Markdown")

async def join_command(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.chat.type != "private": return username = update.message.from_user.username or f"id_{update.message.from_user.id}" user_status[username] = {"status": "joined", "seen": True} save_data() await update.message.reply_text("✅ Tu as rejoint le crossover.")

async def leave_command(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.chat.type != "private": return username = update.message.from_user.username or f"id_{update.message.from_user.id}" user_status[username] = {"status": "ignored", "seen": True} save_data() await update.message.reply_text("🚫 Tu as quitté le crossover.")

async def crossover_now_start(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.chat.type != "private" or update.message.from_user.username != CREATOR_USERNAME: await update.message.reply_text("❗ Commande réservée au créateur, en privé.") return ConversationHandler.END

await update.message.reply_text("🎮 Création du crossover : quel est son *nom* ?")
return CHOOSING_NAME

async def set_name(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["name"] = update.message.text await update.message.reply_text("⏳ Quelle est sa durée (en jours) ?") return CHOOSING_DURATION

async def set_duration(update: Update, context: ContextTypes.DEFAULT_TYPE): try: context.user_data["duration"] = int(update.message.text) await update.message.reply_text("📝 Donne une intro stylée pour ce crossover.") return CHOOSING_INTRO except: await update.message.reply_text("❗ Envoie un nombre valide.") return CHOOSING_DURATION

async def set_intro(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["intro"] = update.message.text await update.message.reply_text("🎯 Quel est l’objectif du crossover ?") return CHOOSING_OBJECTIVE

async def set_objective(update: Update, context: ContextTypes.DEFAULT_TYPE): context.user_data["objective"] = update.message.text await update.message.reply_text("📸 Envoie une photo ou un fichier image.") return CHOOSING_PHOTO

async def set_photo(update: Update, context: ContextTypes.DEFAULT_TYPE): file_id = None if update.message.photo: file_id = update.message.photo[-1].file_id elif update.message.document and update.message.document.mime_type.startswith("image/"): file_id = update.message.document.file_id if not file_id: await update.message.reply_text("❗ Merci d’envoyer une image.") return CHOOSING_PHOTO

context.user_data["photo"] = file_id
end = datetime.now() + timedelta(days=context.user_data["duration"])
context.user_data["end"] = end.strftime("%d/%m/%Y %H:%M")

crossover_data.clear()
crossover_data.update(context.user_data)
user_status.clear()
save_data()

await update.message.reply_text("✅ Crossover enregistré avec succès !")
return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("❌ Création annulée.") return ConversationHandler.END

async def modify_crossover(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.chat.type != "private" or update.message.from_user.username != CREATOR_USERNAME: await update.message.reply_text("❗ Commande réservée au créateur en privé.") return ConversationHandler.END if not crossover_data: await update.message.reply_text("⚠️ Aucun crossover à modifier.") return ConversationHandler.END

await update.message.reply_text("✏️ Que veux-tu modifier ? (nom, intro, objectif, durée)")
return MODIFY_SELECT

async def modify_select(update: Update, context: ContextTypes.DEFAULT_TYPE): field = update.message.text.lower() if field not in ["nom", "intro", "objectif", "durée"]: await update.message.reply_text("❗ Choix invalide. (nom, intro, objectif, durée)") return MODIFY_SELECT context.user_data["field"] = field await update.message.reply_text(f"✏️ Envoie la nouvelle valeur pour {field}.", parse_mode="Markdown") return MODIFY_INPUT

async def modify_input(update: Update, context: ContextTypes.DEFAULT_TYPE): field = context.user_data["field"] value = update.message.text

if field == "durée":
    try:
        value = int(value)
        crossover_data["duration"] = value
        end = datetime.now() + timedelta(days=value)
        crossover_data["end"] = end.strftime("%d/%m/%Y %H:%M")
    except:
        await update.message.reply_text("❗ Durée invalide.")
        return MODIFY_INPUT
elif field == "nom":
    crossover_data["name"] = value
elif field == "intro":
    crossover_data["intro"] = value
elif field == "objectif":
    crossover_data["objective"] = value

save_data()
await update.message.reply_text("✅ Modifié avec succès.")
return ConversationHandler.END

async def delete_crossover(update: Update, context: ContextTypes.DEFAULT_TYPE): if update.message.chat.type != "private" or update.message.from_user.username != CREATOR_USERNAME: await update.message.reply_text("❗ Commande réservée au créateur, en privé.") return

if not crossover_data:
    await update.message.reply_text("⚠️ Aucun crossover actif.")
    return

crossover_data.clear()
user_status.clear()
save_data()
await update.message.reply_text("🗑 Crossover supprimé avec succès.")

async def main(): load_data() app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("crossover", crossover_command))
app.add_handler(CommandHandler("participants", participants_command))
app.add_handler(CommandHandler("joinCross", join_command))
app.add_handler(CommandHandler("leaveCross", leave_command))
app.add_handler(CommandHandler("deleteCrossover", delete_crossover))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("crossoverNow", crossover_now_start)],
    states={
        CHOOSING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_name)],
        CHOOSING_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_duration)],
        CHOOSING_INTRO: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_intro)],
        CHOOSING_OBJECTIVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_objective)],
        CHOOSING_PHOTO: [MessageHandler(filters.PHOTO | filters.Document.IMAGE, set_photo)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("modifierCrossover", modify_crossover)],
    states={
        MODIFY_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, modify_select)],
        MODIFY_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, modify_input)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
))

app.add_handler(CallbackQueryHandler(handle_join, pattern="^join$"))
app.add_handler(CallbackQueryHandler(handle_ignore, pattern="^ignore$"))
app.add_handler(CallbackQueryHandler(handle_close, pattern="^close$"))

await app.run_polling()

if name == "main": import asyncio asyncio.run(main())


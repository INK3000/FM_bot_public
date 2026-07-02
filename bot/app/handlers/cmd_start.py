import betterlogging as logging
from aiogram import Router, types
from aiogram import filters as flt
from aiogram.fsm.context import FSMContext

from .cmd_language import cmd_language

logger = logging.getLogger(__name__)

router = Router()


async def cmd_start(message: types.Message, state: FSMContext) -> None:
    await cmd_language(message, state)


router.message.register(cmd_start, flt.Command("start"))

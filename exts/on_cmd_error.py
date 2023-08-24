import datetime
import importlib

import humanize
import interactions as ipy
from interactions.ext import prefixed_commands as prefixed

import common.utils as utils


class OnCMDError(ipy.Extension):
    def __init__(self, bot: utils.RealmBotBase) -> None:
        self.bot: utils.RealmBotBase = bot

    @staticmethod
    async def handle_send(
        ctx: prefixed.PrefixedContext | ipy.InteractionContext, content: str
    ) -> None:
        embed = utils.error_embed_generate(content)
        if isinstance(ctx, prefixed.PrefixedContext):
            await ctx.reply(embeds=embed)
        else:
            await ctx.send(embeds=embed, ephemeral=ctx.ephemeral)

    @ipy.listen(disable_default_listeners=True)
    async def on_command_error(
        self,
        event: ipy.events.CommandError,
    ) -> None:
        if not isinstance(event.ctx, prefixed.PrefixedContext | ipy.InteractionContext):
            return await utils.error_handle(event.error)

        if isinstance(event.error, ipy.errors.CommandOnCooldown):
            delta_wait = datetime.timedelta(
                seconds=event.error.cooldown.get_cooldown_time()
            )
            await self.handle_send(
                event.ctx,
                "You're doing that command too fast! "
                + "Try again in"
                f" `{humanize.precisedelta(delta_wait, format='%0.1f')}`.",
            )

        elif isinstance(event.error, utils.CustomCheckFailure | ipy.errors.BadArgument):
            await self.handle_send(event.ctx, str(event.error))
        elif isinstance(event.error, ipy.errors.CommandCheckFailure):
            if event.ctx.guild_id:
                await self.handle_send(
                    event.ctx,
                    "You do not have the proper permissions to use that command.",
                )
        else:
            await utils.error_handle(event.error, ctx=event.ctx)


def setup(bot: utils.RealmBotBase) -> None:
    importlib.reload(utils)
    OnCMDError(bot)

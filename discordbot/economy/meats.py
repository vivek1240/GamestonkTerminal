import os

import df2img
import disnake
import pandas as pd
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.economy import finviz_model


async def meats_command(ctx):
    """Displays meats futures data [Finviz]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("econ-meats")

        # Retrieve data
        d_futures = finviz_model.get_futures()
        df = pd.DataFrame(d_futures["Meats"])

        # Check for argument
        if df.empty:
            raise Exception("No available data found")

        df = df.fillna("")
        df = df.set_index("label")
        df = df.sort_values(by="ticker", ascending=False)

        formats = {"last": "${:.2f}", "prevClose": "${:.2f}"}
        for col, value in formats.items():
            df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df)

        df = df[
            [
                "prevClose",
                "last",
                "change",
            ]
        ]
        df.index.names = [""]
        df = df.rename(
            columns={"prevClose": "PrevClose", "last": "Last", "change": "Change"}
        )
        dindex = len(df.index)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(800, (40 + (40 * dindex))),
            col_width=[6, 3, 3],
            tbl_cells=dict(
                align="left",
                height=35,
            ),
            template="plotly_dark",
            font=dict(
                family="Consolas",
                size=20,
            ),
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "econ-meats.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)
        image = disnake.File(imagefile)
        title = "Economy: [Finviz] Meats Futures"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Economy: [Finviz] Meats Futures",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)

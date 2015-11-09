# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from ftfy import fix_text
from ftfy.fixes import fix_encoding_and_explain, apply_plan
from nose.tools import eq_, assert_not_equal


TEST_CASES = [
    # These are excerpts from tweets actually seen on the public Twitter
    # stream. Usernames and links have been removed.

    # Each example is a tuple of:
    # - The minimum cleverness level for the fix to work
    # - The maximum cleverness level for the fix to work (in case of false positives)
    # - The original text
    # - The desired text
    (0, 2, "He's Justinâ¤", "He's Justin❤"),
    (1, 2,
     "Le Schtroumpf Docteur conseille g√¢teaux et baies schtroumpfantes pour un r√©gime √©quilibr√©.",
     "Le Schtroumpf Docteur conseille gâteaux et baies schtroumpfantes pour un régime équilibré."),
    (0, 2, "âœ” No problems", "✔ No problems"),
    (0, 2, '4288×…', '4288×…'),
    (0, 2, 'RETWEET SE VOCÊ…', 'RETWEET SE VOCÊ…'),
    (0, 2, 'PARCE QUE SUR LEURS PLAQUES IL Y MARQUÉ…', 'PARCE QUE SUR LEURS PLAQUES IL Y MARQUÉ…'),
    (0, 2, 'TEM QUE SEGUIR, SDV SÓ…', 'TEM QUE SEGUIR, SDV SÓ…'),
    (0, 2, 'Join ZZAJÉ’s Official Fan List and receive news, events, and more!', "Join ZZAJÉ's Official Fan List and receive news, events, and more!"),
    (0, 2, 'L’épisode 8 est trop fou ouahh', "L'épisode 8 est trop fou ouahh"),
    (1, 2, "РґРѕСЂРѕРіРµ РР·-РїРѕРґ #С„СѓС‚Р±РѕР»", "дороге Из-под #футбол"),
    (0, 2,
     "\x84Handwerk bringt dich \xfcberall hin\x93: Von der YOU bis nach Monaco",
     '"Handwerk bringt dich überall hin": Von der YOU bis nach Monaco'),
    (0, 2, "Hi guys í ½í¸", "Hi guys 😍"),
    (0, 2, "hihi RT username: âºí ½í¸", "hihi RT username: ☺😘"),
    (0, 2, "Beta Haber: HÄ±rsÄ±zÄ± BÃ¼yÃ¼ Korkuttu", "Beta Haber: Hırsızı Büyü Korkuttu"),
    (0, 2, "Ôôô VIDA MINHA", "Ôôô VIDA MINHA"),
    (0, 2, '[x]\xa0©', '[x]\xa0©'),
    (0, 2, '2012—∞', '2012—∞'),
    (0, 2,
     'Con il corpo e lo spirito ammaccato,\xa0è come se nel cuore avessi un vetro conficcato.',
     'Con il corpo e lo spirito ammaccato,\xa0è come se nel cuore avessi un vetro conficcato.'),
    (1, 2, 'Р С—РЎР‚Р С‘РЎРЏРЎвЂљР Р…Р С•РЎРѓРЎвЂљР С‘. РІСњВ¤', 'приятности. ❤'),
    (0, 2, 
     'Kayanya laptopku error deh, soalnya tiap mau ngetik deket-deket kamu font yg keluar selalu Times New Ã¢â‚¬Å“ RomanceÃ¢â‚¬Â.',
     'Kayanya laptopku error deh, soalnya tiap mau ngetik deket-deket kamu font yg keluar selalu Times New " Romance".'),
    (0, 2, "``toda produzida pronta pra assa aí´´", "``toda produzida pronta pra assa aí´´"),
    (0, 2, 'HUHLL Õ…', 'HUHLL Õ…'),
    (0, 2, 'Iggy Pop (nÃƒÂ© Jim Osterberg)', 'Iggy Pop (né Jim Osterberg)'),
    (0, 2,
     'eres mía, mía, mía, no te hagas la loca eso muy bien ya lo sabías',
     'eres mía, mía, mía, no te hagas la loca eso muy bien ya lo sabías'),
    (0, 2,
     "Direzione Pd, ok âsenza modifiche all'Italicum.",
     "Direzione Pd, ok \"senza modifiche\" all'Italicum."),
    (0, 2,
     'Engkau masih yg terindah, indah di dalam hatikuâ™«~',
     'Engkau masih yg terindah, indah di dalam hatiku♫~'),
    (0, 2, 'SENSЕ - Oleg Tsedryk', 'SENSЕ - Oleg Tsedryk'),   # this Е is a Ukrainian letter
    (0, 2, 'OK??:(   `¬´    ):', 'OK??:(   `¬´    ):'),
    (0, 2,
     "selamat berpuasa sob (Ã\xa0Â¸â€¡'ÃŒâ‚¬Ã¢Å’Â£'ÃŒÂ\x81)Ã\xa0Â¸â€¡",
     "selamat berpuasa sob (ง'̀⌣'́)ง"),
    (0, 2, 'Feijoada do Rio Othon Palace no Bossa Café\x80\x80', 'Feijoada do Rio Othon Palace no Bossa Café\x80\x80'),
    (0, 2, "├┤a┼┐a┼┐a┼┐a┼┐a", "├┤a┼┐a┼┐a┼┐a┼┐a"),
    (0, 2, "SELKÄ\xa0EDELLÄ\xa0MAAHAN via @YouTube", "SELKÄ\xa0EDELLÄ\xa0MAAHAN via @YouTube"),
    (0, 2, 'WELCΘME HΘME THETAS!', 'WELCΘME HΘME THETAS!'),

    # This one has two differently-broken layers of Windows-1252 <=> UTF-8,
    # and it's kind of amazing that we solve it.
    (1, 2, 
     'Arsenal v Wolfsburg: pre-season friendly â\x80â\x80\x9c live!',
     'Arsenal v Wolfsburg: pre-season friendly – live!'),

    # Test that we can mostly decode this face when the nonprintable
    # character \x9d is lost
    (0, 2, 'Ã¢â€\x9dâ€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€\x9dÅ½', '┒(⌣˛⌣)┎'),
    (0, 2, 'Ã¢â€�â€™(Ã¢Å’Â£Ã‹â€ºÃ¢Å’Â£)Ã¢â€�Å½', '�(⌣˛⌣)�'),

    # You tried
    (0, 2,
     'I just figured out how to tweet emojis! â\x9a½í\xa0½í¸\x80í\xa0½í¸\x81í\xa0½í¸\x82í\xa0½í¸\x86í\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8eí\xa0½í¸\x8e',
     'I just figured out how to tweet emojis! ⚽😀😁😂😆😎😎😎😎'),

    # Fix single-byte encoding mixups
    (2, 2,
     'Inglaterra: Es un lugar que nunca te aburrir‡s',
     'Inglaterra: Es un lugar que nunca te aburrirás'),
    (2, 2,
     'Inundaciones y da\x96os materiales en Tamaulipas por lluvias',
     'Inundaciones y daños materiales en Tamaulipas por lluvias'),
    (2, 2, 'èíñòðóêöèÿ', 'инструкция'),

    # Examples from martinblech
    (2, 2, 'ÖÉËÁ ÌÅ - ÂÏÓÊÏÐÏÕËÏÓ - ×ÉÙÔÇÓ', 'ΦΙΛΑ ΜΕ - ΒΟΣΚΟΠΟΥΛΟΣ - ΧΙΩΤΗΣ'),
    (2, 2, 'ÑÅÊÐÅÒ - Áåñïå÷íûé Åçäîê - 0:00', 'СЕКРЕТ - Беспечный Ездок - 0:00'),

    # ISO-8859-1(?) / cp437 mojibake on top of Romanized Urdu leetspeak.
    # This is such a crazy solution that I won't even mind if it regresses.
    (2, 2, 
     '""" JUMMA """"    ,M\x97B\x84R\x84K ,   " H\x94"AP"K\x94 D\x97\x84 h\x84i \x8ds M\x97b\x84r\x84k D\x8dn k S\x84dq\x8a A\x84p k\x8d H\x84r p\x84r\x8ash\x84n\x8d A\x97r H\x84r M\x97sib\x84t d\x94\x94r H\x94 J\x84y\x8a    =AAMEEn=',
     '""" JUMMA """"    ,MùBäRäK ,   " Hö"AP"Kö Dùä häi ìs Mùbäräk Dìn k Sädqè Aäp kì Här pärèshänì Aùr Här Mùsibät döör Hö Jäyè    =AAMEEn='),

    # We can fix the character width here. This also looks plausibly like
    # Shift-JIS/EUC-JP mojibake, although it isn't. If we ever become able
    # to fix that particular mix-up, make sure this text isn't wrongly "fixed".
    (0, 2, '(|| * m *)ｳ､ｳｯﾌﾟ･･', '(|| * m *)ウ、ウップ・・'),

    ## Current false positives:
    #(0, 2, "ESSE CARA AI QUEM É¿", "ESSE CARA AI QUEM É¿"),
    #(0, 2, "``hogwarts nao existe, voce nao vai pegar o trem pra lá´´", "``hogwarts nao existe, voce nao vai pegar o trem pra lá´´"),
    #(0, 2, 'P I R Ê™', 'P I R Ê™'),

    ## We don't try to fix East Asian mojibake yet, but here are some examples:
    ## Windows-1252/EUC-JP
    #(3, 3, '49Ç¯Á°½Ð¾ì¡¢Ê¡¸¶¤µ¤ó¤â´î¤Ó Åìµþ¸ÞÎØ ¡Ê¤ï¤«¤ä¤Þ¿·Êó¡Ë',
    #       '49年前出場、福原さんも喜び 東京五輪 (わかやま新報)'),

    ## Latin-1/Shift-JIS
    #(3, 3, '\x83o\x83{\x82¿\x82á\x82ñ\x83l\x83b\x83g\x83j\x83\x85\x81[\x83X',
    #       'バボちゃんネットニュース'),

    ## Windows-1252/EUC-KR
    #(3, 3, '¼Ò¸®¿¤ - »ç¶ûÇÏ´Â ÀÚ¿©', '소리엘 - 사랑하는 자여'),

    ## The heuristics aren't confident enough to fix these examples:
    #(1, 2, 
    # "Blog Traffic Tip 2 вЂ“ Broadcast Email Your Blog",
    # "Blog Traffic Tip 2 – Broadcast Email Your Blog"),
    #(2, 2,
    # "Deja dos heridos hundimiento de barco tur\x92stico en Acapulco.",
    # "Deja dos heridos hundimiento de barco turístico en Acapulco."),

    ## Can't fix this because we're cautious about false positives involving \xa0.
    #(0, 2, 'CÃ\xa0nan nan GÃ\xa0idheal', 'Cànan nan Gàidheal'),
]


def test_real_tweets():
    """
    Test with text actually found on Twitter.

    I collected these test cases by listening to the Twitter streaming API for
    a million or so tweets, picking out examples with high weirdness according
    to ftfy version 2, and seeing what ftfy decoded them to. There are some
    impressive things that can happen to text, even in an ecosystem that is
    supposedly entirely UTF-8.

    The tweets that appear in TEST_CASES are the most interesting examples of
    these, with some trickiness of how to decode them into the actually intended
    text.
    """
    for min_cleverness, max_cleverness, orig, target in TEST_CASES:
        for cleverness in range(3):
            # make sure that the fix_encoding step outputs a plan that we can
            # successfully run to reproduce its result
            encoding_fix, plan = fix_encoding_and_explain(orig, cleverness=cleverness)
            eq_(apply_plan(orig, plan), encoding_fix)

            fixed = fix_text(orig, cleverness=cleverness)
            if min_cleverness <= cleverness <= max_cleverness:
                # make sure we can decode the text as intended
                eq_(fixed, target)

                # make sure we can decode as intended even with an extra layer of badness
                extra_bad = orig.encode('utf-8').decode('latin-1')
                eq_(fix_text(extra_bad, cleverness=2), target)
            else:
                # make sure it's right to give up at this level of cleverness
                assert_not_equal(fixed, target)

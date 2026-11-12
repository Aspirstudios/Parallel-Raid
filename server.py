# Parallel Raid  -  servidor dedicado (sin ventana)
import os, sys, random, argparse, threading, time, traceback, queue, zlib

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

try:
    import paralel_raid as game
except Exception as e:
    print("=" * 60)
    print("ERROR CRÍTICO AL CARGAR 'paralel_raid.py'")
    print("=" * 60)
    print(f"Motivo: {e}")
    print("-" * 60)
    traceback.print_exc()
    print("=" * 60)
    print("POSIBLE SOLUCIÓN: Abre la consola y ejecuta -> pip install pygame")
    sys.exit(1)

print(f"[SERVER] paralel_raid.py cargado desde: {os.path.abspath(game.__file__)}")
if getattr(game, "NET_BUILD", None) != "udp-v5":
    print("AVISO: este paralel_raid.py no es udp-v5; se arranca igualmente (protecciones desactivadas).")

TICK = 1.0 / 60.0          # 60 ticks/s fijos

cmds = queue.Queue()       # la consola solo ENCOLA; el bucle principal ejecuta


def command_listener():
    print("[CMD] Consola lista. Escribe 'help' para ver comandos.")
    while True:
        try:
            cmd = input().strip()
        except EOFError:
            break
        except Exception as e:
            print(f"[CMD] Error: {e}")
            continue
        if cmd:
            cmds.put(cmd)


def techos_ligeros():
    """Mismos rectángulos de techo que el cliente, pero sin dibujar superficies."""
    T = game.TILE
    return [(tx * T, ty * T, tx, ty, tw, th, None)
            for (tx, ty, tw, th) in game.CUR.get("interiors", [])]


def asignar_humanos():
    """new_round() recrea TODOS los actores como bots: aquí se devuelve cada humano a su hueco."""
    for a in game.actors:
        if a.player and not hasattr(a, "_netid"):
            a.player = False
            a.name = game.NAMES[a.team][a.slot]
    usados = set()
    for pid, cl in list(game.NET.clients.items()):
        a = next((x for x in game.actors if x.team == cl.get("team") and x.slot == cl.get("slot")
                  and id(x) not in usados), None)
        if a is None:
            a = next((x for x in game.actors if id(x) not in usados), None)
        if a is None:
            game.lan_server_remove(pid)
            continue
        usados.add(id(a))
        a.player = True
        a._netid = pid
        a.name = cl.get("name", a.name)
        cl["team"], cl["slot"] = a.team, a.slot


def nueva_ronda():
    game.new_round()
    asignar_humanos()


# ----------------------------------------------------------------------------------------------
# PARCHES DE COMPATIBILIDAD
# ----------------------------------------------------------------------------------------------
_BOT_AI_SRC = r'''
def bot_ai(a, dt):
    weapon_tick(a, dt)
    a.moving = False
    if a.mag == 0:
        start_reload(a)
    a.vis_t -= dt
    a.alert_t -= dt
    if a.alert_src is not None and (a.alert_t <= 0 or not a.alert_src.alive):
        a.alert_src, a.alert_t = None, 0.0
    if a.vis_t <= 0:
        a.vis_t = .08
        best, bd = None, VIS
        for e in actors:
            if e.alive and e.team != a.team:
                d = math.hypot(e.x - a.x, e.y - a.y)
                exposed = e is a.alert_src
                if d < bd and los(a.x, a.y, e.x, e.y) and (exposed or not (roof_of(e) is not None and roof_of(a) is None)):
                    best, bd = e, d
        if best is not None and best is not a.target:
            a.react = random.uniform(.35, .7)
            a.burst = 0
        a.target = best
    e = a.target
    if e is not None and e.alive:
        dx, dy = e.x - a.x, e.y - a.y
        d = max(1.0, math.hypot(dx, dy))
        want = math.atan2(dy, dx)
        a.ang = turn(a.ang, want, 8 * dt)
        a.react -= dt
        aimed = abs(angdiff(a.ang, want)) < .25
        if a.react <= 0 and aimed and d <= a.W["reach"]:
            if a.burst > 0:
                if shoot(a, .02):
                    a.burst -= 1
                    if a.burst == 0:
                        a.cool = max(a.cool, random.uniform(.4, .9))
            elif a.cool <= 0:
                a.burst = random.randint(*a.W["burst"])
        a.strafe_t -= dt
        if a.strafe_t <= 0:
            a.strafe = random.choice((-1, 0, 1))
            a.strafe_t = random.uniform(.4, 1.0)
        if d > a.W["rng"]:
            sx, sy = dx / d * .5, dy / d * .5
        else:
            sx, sy = -dy / d * a.strafe * .6, dx / d * a.strafe * .6
        a.moving = bool(sx or sy)
        move_actor(a, sx * BOT_SPEED * a.W["spd"] * dt, sy * BOT_SPEED * a.W["spd"] * dt)
        a.act = 0.0
        return
    a.target = None
    a.burst = 0
    goal = bot_goal(a)
    if (a.alert_src is not None and a.alert_t > 0 and a is not G.defuser
            and not (a.team == "T" and a is G.planter)):
        goal = tile_of(a.alert_src.x, a.alert_src.y)
    gx, gy = center(goal)
    moving = False
    if math.hypot(gx - a.x, gy - a.y) > 6:
        moving = step_towards(a, goal, dt)
    a.moving = moving
    if not moving:
        a.look_t -= dt
        if a.look_t <= 0:
            if bomb.planted:
                base = math.atan2(bomb.y - a.y, bomb.x - a.x)
            else:
                base = 0.0 if a.team == "T" else math.pi
            a.look = base + random.uniform(-.9, .9)
            a.look_t = random.uniform(1, 2.5)
        a.ang = turn(a.ang, a.look, 3 * dt)
    planting = (a.team == "T" and a is G.planter and not bomb.planted
                and site_at(a.x, a.y) and math.hypot(gx - a.x, gy - a.y) < 25)
    if planting:
        a.act += dt
        if a.act >= PLANT_T:
            plant(a.x, a.y, a)
            a.act = 0.0
    else:
        a.act = 0.0
    if a.team == "CT" and bomb.planted and a is G.defuser and math.hypot(bomb.x - a.x, bomb.y - a.y) < 30:
        a.defusing = True
'''

_ALERT_BOT_SRC = r'''
def alert_bot(b, src, secs=5.0):
    if b.player or hasattr(b, "_netid") or not b.alive or src is None or not src.alive:
        return
    if b.alert_src is not src or b.alert_t <= 0:
        b.react = min(b.react, random.uniform(.2, .4)) if b.react > 0 else 0.0
    b.alert_src, b.alert_t = src, secs
'''

def sin_protecciones(game):
    class _Sock:
        def __init__(self, s):
            self._s = s
            self.ep = None
        def recvfrom(self, n):
            data, ep = self._s.recvfrom(n)
            self.ep = ep
            return data, ep
        def __getattr__(self, k):
            return getattr(self._s, k)

    sock = _Sock(game.NET.listener)
    game.NET.listener = sock
    builds = {}

    unpk0 = game._unpk
    def _unpk(b):
        m = unpk0(b)
        if isinstance(m, dict) and "build" in m:
            builds[sock.ep] = m["build"]
            m["build"] = game.NET_BUILD
        return m
    game._unpk = _unpk

    send0 = game._sv_send
    def _sv_send(ep, d):
        if isinstance(d, dict):
            d = dict(d)
            d.pop("gh", None)
            if "build" in d and ep in builds:
                d["build"] = builds[ep]
        return send0(ep, d)
    game._sv_send = _sv_send


def huella():
    return zlib.crc32(bytes(v for row in game.grid for v in row))


def aplicar_parches(game):
    import math
    hecho = []
    if hasattr(game, "alert_bot"):
        return hecho

    if "door_clear" not in game.MAPDEFS["cache"]:
        game.MAPDEFS["cache"]["door_clear"] = 1
        hecho.append("cache: puertas despejadas")
    ag = game.MAPDEFS["agency"]
    if "door_clear" not in ag:
        sala = tuple(game._scale_rect((38, 28, 6, 8)))
        lados = ag.get("door_sides", {}).get(sala)
        if lados is not None and "east" not in lados:
            ag["door_sides"][sala] = tuple(lados) + ("east",)
        ag.update(door_clear=1, lush=.25, floor=(132, 140, 152), floor_style="office", room_floor="carpet",
                  desc="Agencia: edificio de cristal con atrio y estanque")
        game.NATURE["agency"] = "city"
        hecho.append("agency: puerta este, poca vegetacion, suelo de oficina, puertas despejadas")
    if not getattr(game, "_door_zone_parcheada", False):
        orig_dz = game.door_zone
        def door_zone(d, r=2):
            return orig_dz(d, max(r, d.get("door_clear", 0)))
        game.door_zone = door_zone
        game._door_zone_parcheada = True

    if not hasattr(game, "alert_bot"):
        ns = game.__dict__
        exec(_ALERT_BOT_SRC, ns)
        exec(_BOT_AI_SRC, ns)

        init0 = game.Actor.__init__
        def init(self, *a, **k):
            init0(self, *a, **k)
            self.alert_src, self.alert_t = None, 0.0
        game.Actor.__init__ = init

        shoot0 = game.shoot
        def shoot(a, base):
            ok = shoot0(a, base)
            if ok and game.roof_of(a) is not None:
                for e in game.actors:
                    if e.alive and e.team != a.team and not e.player and game.roof_of(e) is None:
                        d = math.hypot(e.x - a.x, e.y - a.y)
                        if d < game.VIS * 1.2 and game.los(e.x, e.y, a.x, a.y):
                            game.alert_bot(e, a, 4.0)
            return ok
        game.shoot = shoot

        damage0 = game.damage
        def damage(a, dmg, owner):
            damage0(a, dmg, owner)
            if owner is not None and owner.alive and owner.team != a.team:
                game.alert_bot(a, owner, 6.0)
        game.damage = damage
        hecho.append("IA de bots: reaccion al fuego desde zonas techadas")
    return hecho


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default=None, help="clave de mapa (ver 'maps')")
    ap.add_argument("--name", default="Parallel Raid Server", help="nombre en la lista de servidores")
    ap.add_argument("--con-comprobacion", action="store_true", help="enviar la huella de la rejilla")
    ap.add_argument("--sin-parches", action="store_true", help="no aplicar los parches de compatibilidad")
    args = ap.parse_args()

    print("=" * 50)
    print("       PARALLEL RAID - SERVIDOR DEDICADO - CONSOLA")
    print("=" * 50)

    game.build_world = lambda: game.pygame.Surface((1, 1))
    game.build_interior_roofs = techos_ligeros
    if hasattr(game, "draw_game"):
        game.draw_game = lambda: None

    game.lan_server_start()
    if not args.con_comprobacion:
        sin_protecciones(game)
        print("[SERVER] Protecciones DESACTIVADAS: sin huella de mapa y sin comprobacion de version.")

    if args.sin_parches:
        print("[SERVER] Parches de compatibilidad DESACTIVADOS.")
    else:
        aplicados = aplicar_parches(game)
        if aplicados:
            for linea in aplicados:
                print(f"[SERVER] Parche aplicado -> {linea}")
        else:
            print("[SERVER] Este paralel_raid.py ya incluye los cambios; no hace falta parchear.")

    game.NET.is_server = True
    game.NET.server_name = args.name
    game.WIN_SCORE = 6

    mapas = list(game.MAPDEFS.keys())
    estado = {"mapa": args.map if args.map in game.MAPDEFS else random.choice(mapas)}
    if args.map and args.map not in game.MAPDEFS:
        print(f"[SERVER] Mapa '{args.map}' no existe, uso '{estado['mapa']}'. Mapas: {', '.join(mapas)}")

    def cargar_nuevo_mapa(clave):
        if clave not in game.MAPDEFS:
            print(f"[SERVER] Mapa desconocido: {clave}. Mapas: {', '.join(mapas)}")
            return
        print(f"\n[SERVER] >>> Cargando mapa: {clave}")
        try:
            game.load_map(clave)
            estado["mapa"] = clave
            game.G.team = "T"
            game.reset_economy()
            game.G.score_t = game.G.score_ct = game.G.kills = 0
            game.G.round_no = 0
            nueva_ronda()
            print(f"[SERVER] >>> Nueva partida iniciada. Huella de la rejilla de '{clave}': {huella()}")
        except Exception:
            print(f"[SERVER] Error cargando mapa {clave}:")
            traceback.print_exc()

    def ejecutar(cmd):
        partes = cmd.split(" ", 1)
        acc = partes[0].lower()
        arg = partes[1].strip() if len(partes) > 1 else ""
        N = game.NET
        if acc == "help":
            print("[CMD] status, huellas, maps, map <clave>, rotate, restart, kick <id>, say <texto>, stop")
        elif acc == "status":
            print(f"[CMD] Mapa: {estado['mapa']} | ronda {game.G.round_no} | T {game.G.score_t} - CT {game.G.score_ct}")
            print(f"[CMD] Huella de la rejilla: {zlib.crc32(bytes(v for row in game.grid for v in row))}")
            print(f"[CMD] Jugadores: {len(N.clients)}")
            for pid, cl in N.clients.items():
                print(f"[CMD]   - ID {pid}: {cl.get('name')} ({cl.get('team')}) desde {cl.get('addr')}")
        elif acc == "huellas":
            actual = estado["mapa"]
            for m in mapas:
                game.load_map(m)
                print(f"[CMD] {m}: {huella()}")
            game.load_map(actual)
        elif acc == "maps":
            print("[CMD] " + ", ".join(mapas))
        elif acc == "map" and arg:
            cargar_nuevo_mapa(arg)
        elif acc == "rotate":
            cargar_nuevo_mapa(random.choice(mapas))
        elif acc == "restart":
            cargar_nuevo_mapa(estado["mapa"])
        elif acc == "kick" and arg:
            try:
                pid = int(arg)
            except ValueError:
                print("[CMD] Uso: kick <id>")
                return
            if pid in N.clients:
                game.lan_server_remove(pid)
                print(f"[CMD] Jugador {pid} expulsado.")
            else:
                print("[CMD] ID no encontrado.")
        elif acc == "say" and arg:
            for pid in list(N.clients):
                game.lan_server_queue(pid, {"type": "msg", "text": arg})
            print(f"[CMD] Enviado: {arg}")
        elif acc == "stop":
            print("[CMD] Apagando servidor...")
            os._exit(0)
        else:
            print("[CMD] Comando no reconocido. Escribe 'help'.")

    cargar_nuevo_mapa(estado["mapa"])
    threading.Thread(target=command_listener, daemon=True).start()
    print("[SERVER] Servidor listo (60 Hz).")

    G = game.G
    siguiente = time.perf_counter()
    last = siguiente
    match_over_t = None
    lentos = 0
    acum = 0.0
    st_sum = 0.0; st_n = 0; st_max = 0.0; st_t = time.perf_counter()
    errores = 0

    try:
        while True:
            while True:
                try:
                    c = cmds.get_nowait()
                except queue.Empty:
                    break
                try:
                    ejecutar(c)
                except Exception:
                    traceback.print_exc()

            ahora = time.perf_counter()
            acum += min(ahora - last, 0.25)
            last = ahora
            G.t = time.time()

            try:
                game.lan_server_tick()
                pasos = 0
                while acum >= TICK and pasos < 4:
                    acum -= TICK
                    pasos += 1
                    dt = TICK
                    if G.state == "freeze":
                        G.timer -= dt
                        if G.timer <= 0:
                            G.state = "live"
                    elif G.state == "live":
                        game.run_live(dt)
                    elif G.state == "over":
                        G.timer -= dt
                        if G.timer <= 0:
                            if max(G.score_t, G.score_ct) >= game.WIN_SCORE:
                                G.state = "matchover"
                                match_over_t = time.time()
                            else:
                                nueva_ronda()
                    elif G.state == "matchover":
                        if match_over_t is None:
                            match_over_t = time.time()
                        if time.time() - match_over_t > 8.0:
                            match_over_t = None
                            cargar_nuevo_mapa(random.choice(mapas))
                    game.update_fx(dt)
                if pasos == 4:
                    acum = 0.0
            except Exception:
                errores += 1
                if errores <= 20:
                    traceback.print_exc()

            ms = (time.perf_counter() - ahora) * 1000
            st_sum += ms; st_n += 1; st_max = max(st_max, ms)
            if time.perf_counter() - st_t > 10.0:
                print(f"[SERVER] {len(game.NET.clients)} jug. | tick medio {st_sum/st_n:.1f} ms, max {st_max:.1f} ms (limite 16.7)")
                st_sum = st_n = 0; st_max = 0.0; st_t = time.perf_counter()

            siguiente += TICK
            espera = siguiente - time.perf_counter()
            if espera > 0:
                if espera > 0.003:
                    time.sleep(espera - 0.002)
                while time.perf_counter() < siguiente:
                    pass
            else:
                if espera < -0.25:
                    siguiente = time.perf_counter()
                lentos += 1
                if lentos % 120 == 1:
                    print(f"[SERVER] tick lento ({-espera*1000:.0f} ms de retraso)")
    except KeyboardInterrupt:
        print("\n[SERVER] Cerrando...")
        sys.exit(0)


if __name__ == "__main__":
    main()
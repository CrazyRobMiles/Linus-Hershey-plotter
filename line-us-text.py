#!/usr/bin/python
# Send text to the line-us printer
# Rob Miles 2018-09-10 www.robmiles.com
# Version 1.0
#
# based on:
# turtle-hershey-example - a trivial demo to say hello
# scruss - 2014-05-06 - dual WTFPL (srsly)

import socket
import time

class LineUs:
    verbose = False
    command_debug = False
    __x_offset = 790
    max_x = 900.0
    __x_min = 0
    __y_offset = -900
    max_y = 1790.0
    __y_min = 0

    __x_pos = 0
    __y_pos = 0

    def __init__(self, line_us_name):
        if self.verbose:
            print("Opening socket")
        self.__line_us = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__line_us.connect((line_us_name, 1337))
        self.__connected = True
        self.__hello_message = self.__read_response()
        self.__up = False

    def get_hello_string(self):
        if self.verbose:
            print("Get hello string")
        if self.__connected:
            return self.__hello_message.decode()
        else:
            return 'Not connected'

    def disconnect(self):
        """Close the connection to the Line-us"""
        if self.verbose:
            print("Disconnect")
        self.__line_us.close()
        self.__connected = False

    def g01(self, x, y, z):
        """Send a G01 (interpolated move), and wait for the response before returning"""
        cmd = b'G01 X'
        cmd += str(int(x+0.5)).encode()
        cmd += b' Y'
        cmd += str(int(y+0.5)).encode()
        cmd += b' Z'
        cmd += str(int(z+0.5)).encode()
        self.__send_command(cmd)
        self.__read_response()

    def up(self):
        if self.verbose:
            print("up")
        if self.__up:
            return
        self.__up = True
        cmd = b'G01 Z1000'
        self.__send_command(cmd)
        self.__read_response()
        time.sleep(0.5)
        
    def down(self):
        if self.verbose:
            print("down")
        if not self.__up:
            return
        self.__up = False
        cmd = b'G01 Z0'
        self.__send_command(cmd)
        self.__read_response()

    def check_coords(self,x,y):
        if x>self.max_x:
            x = self.max_x
        if x<self.__x_min:
            x = self.__x_min
        x = x+self.__x_offset
        if y>self.max_y:
            y = self.max_y
        if y<self.__y_min:
            y = self.__y_min
        y = y+self.__y_offset
        return (x,y)
        
    def move(self, x, y):
        self.__x_pos = x
        self.__y_pos = y
        x,y = self.check_coords(x,y)
        self.up()
        if self.verbose:
            print("move x:",x," y:", y)
        self.g01(x,y,1000)

    def draw(self,x,y):
        self.__x_pos = x
        self.__y_pos = y
        x,y = self.check_coords(x,y)
        self.down()
        if self.verbose:
            print("draw x:",x," y:", y)
        self.g01(x,y,0)

    def draw_relative(self,x,y):
        if self.verbose:
            print("draw relative x:",x," y:", y)
        self.__x_pos = self.__x_pos + x
        self.__y_pos = self.__y_pos + y
        self.draw(self.__x_pos, self.__y_pos)

    def move_relative(self,x,y):
        if self.verbose:
            print("move relative x:",x," y:", y)
        self.__x_pos = self.__x_pos + x
        self.__y_pos = self.__y_pos + y
        self.move(self.__x_pos, self.__y_pos)

    def __read_response(self):
        """Read from the socket one byte at a time until we get a null"""
        line = b''
        while True:
            char = self.__line_us.recv(1)
            if char != b'\x00':
                line += char
            elif char == b'\x00':
                break
        return line

    def __send_command(self, command):
        """Send the command to Line-us"""
        if self.command_debug:
            print(str(command))
        command += b'\x00'
        self.__line_us.send(command)

    def home(self):
        if self.verbose:
            print("home")
        cmd = b'G28'
        self.__send_command(cmd)
        self.__read_response()
        self.__x_pos = 0
        self.__y_pos = 0

    def setup_pen(self):
        self.up()
        self.home()
        self.down()
        input('Set the pen height and press Enter')
        self.up()
        
def char2val(c):  # data is stored as signed bytes relative to ASCII R
    return ord(c) - ord('R')

def identity(a,b):
    return [a,b]

def hersheyparse(dat):
    """ reads a line of Hershey font text """

    if int(dat[5:8]) - 1 < 2:  # fail if there impossibly few vertices
        return None
    lines = []

    # individual lines are stored separated by <space>+R
    # starting at col 11
    for s in str.split(dat[10:], ' R'):
        # each line is a list of pairs of coordinates
        # NB: origin is at centre(ish) of character
        #     Y coordinates **increase** downwards
        line = map(identity, *[iter(map(char2val, list(s)))] * 2)
        lines.append(line)
    glyph = {  # character code in columns 1-6; it's not ASCII
               # indicative number of vertices in columns 6-9
               # left side bearing encoded in column 9
               # right side bearing encoded in column 10
        'charcode': int(dat[0:5]),
        'vertices': int(dat[5:8]) - 1,
        'left': char2val(dat[8]),
        'right': char2val(dat[9]),
        'lines': lines,
        }
    return glyph


# a hash for the four chars we're going to use: they're cursive

script_glyphs = {
    'A': '  551 20G[G[IZLWOSSLVFV[UXSUQSNQLQKRKTLVNXQZT[Y[',
    'B': '  552 41F]SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFXFZG[I[KZMYNWOTP RSPTPWQXRYTYWXYWZU[R[PZOX',
    'C': '  553 24H\TLTMUNWNYMZKZIYGWFTFQGOIMLLNKRKVLYMZO[Q[TZVXWV',
    'D': '  554 35G^TFRGQIPMOSNVMXKZI[G[FZFXGWIWKXMZP[S[VZXXZT[O[KZHYGWFTFRHRJSMUPWRZT\\U',
    'E': '  555 28H\VJVKWLYLZKZIYGVFRFOGNINLONPOSPPPMQLRKTKWLYMZP[S[VZXXYV',
    'F': '  556 28H\RLPLNKMINGQFTFXG[G]F RXGVNTTRXPZN[L[JZIXIVJULUNV RQPZP',
    'G': '  557 29G^G[IZMVPQQNRJRGQFPFOGNINLONQOUOXNYMZKZQYVXXVZS[O[LZJXIVIT',
    'H': '  558 38F^MMKLJJJIKGMFNFPGQIQKPONULYJ[H[GZGX RMRVOXN[L]J^H^G]F\FZHXLVRUWUZV[W[YZZY\V',
    'I': '  559 25IZWVUTSQROQLQIRGSFUFVGWIWLVQTVSXQZO[M[KZJXJVKUMUOV',
    'J': '  560 25JYT^R[PVOPOJPGRFTFUGVJVMURR[PaOdNfLgKfKdLaN^P\SZWX',
    'K': '  561 39F^MMKLJJJIKGMFNFPGQIQKPONULYJ[H[GZGX R^I^G]F\FZGXIVLTNROPO RROSQSXTZU[V[XZYY[V',
    'L': '  562 29I\MRORSQVOXMYKYHXFVFUGTISNRSQVPXNZL[J[IZIXJWLWNXQZT[V[YZ[X',
    'M': '  563 45@aEMCLBJBICGEFFFHGIIIKHPGTE[ RGTJLLHMGOFPFRGSISKRPQTO[ RQTTLVHWGYFZF\G]I]K\PZWZZ[[\[^Z_YaV',
    'N': '  564 32E]JMHLGJGIHGJFKFMGNINKMPLTJ[ RLTOLQHRGTFVFXGYIYKXPVWVZW[X[ZZ[Y]V',
    'O': '  565 29H]TFQGOIMLLNKRKVLYMZO[Q[TZVXXUYSZOZKYHXGVFTFRHRKSNUQWSZU\V',
    'P': '  566 31F_SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFZF\G]H^J^M]O\PZQWQUPTO',
    'Q': '  567 32H^ULTNSOQPOPNNNLOIQGTFWFYGZIZMYPWSSWPYNZK[I[HZHXIWKWMXPZS[V[YZ[X',
    'R': '  568 38F_SHTITLSPRSQUOXMZK[J[IZIWJRKOLMNJPHRGUFYF[G\H]J]M\O[PYQVQSPTQUSUXVZX[ZZ[Y]V',
    'S': '  569 28H\H[JZLXOTQQSMTJTGSFRFQGPIPKQMSOVQXSYUYWXYWZT[P[MZKXJVJT',
    'T': '  570 25H[RLPLNKMINGQFTFXG[G]F RXGVNTTRXPZN[L[JZIXIVJULUNV',
    'U': '  571 33E]JMHLGJGIHGJFKFMGNINKMOLRKVKXLZN[P[RZSYUUXMZF RXMWQVWVZW[X[ZZ[Y]V',
    'V': '  572 32F]KMILHJHIIGKFLFNGOIOKNOMRLVLYM[O[QZTWVTXPYMZIZGYFXFWGVIVKWNYP[Q',
    'W': '  573 25C_HMFLEJEIFGHFIFKGLILLK[ RUFK[ RUFS[ RaF_G\JYNVTS[',
    'X': '  574 36F^NLLLKKKILGNFPFRGSISLQUQXRZT[V[XZYXYVXUVU R]I]G\FZFXGVITLPUNXLZJ[H[GZGX',
    'Y': '  575 38F]KMILHJHIIGKFLFNGOIOKNOMRLVLXMZN[P[RZTXVUWSYM R[FYMVWT]RbPfNgMfMdNaP^S[VY[V',
    'Z': '  576 40H]ULTNSOQPOPNNNLOIQGTFWFYGZIZMYPWTTWPZN[K[JZJXKWNWPXQYR[R^QaPcNfLgKfKdLaN^Q[TYZV',

    'a': '  651 22L\\UUTSRRPRNSMTLVLXMZO[Q[SZTXVRUWUZV[W[YZZY\\V',
    'b': '  652 23M[MVOSRNSLTITGSFQGPIOMNTNZO[P[RZTXUUURVVWWYW[V',
    'c': '  653 14MXTTTSSRQROSNTMVMXNZP[S[VYXV',
    'd': '  654 24L\\UUTSRRPRNSMTLVLXMZO[Q[SZTXZF RVRUWUZV[W[YZZY\V',
    'e': '  655 17NXOYQXRWSUSSRRQROSNUNXOZQ[S[UZVYXV',
    'f': '  656 24OWOVSQUNVLWIWGVFTGSIQQNZKaJdJfKgMfNcOZP[R[TZUYWV',
    'g': '  657 28L[UUTSRRPRNSMTLVLXMZO[Q[SZTY RVRTYPdOfMgLfLdMaP^S\\U[XY[V',
    'h': '  658 29M\MVOSRNSLTITGSFQGPIOMNSM[ RM[NXOVQSSRURVSVUUXUZV[W[YZZY\\V',
    'i': '  659 16PWSMSNTNTMSM RPVRRPXPZQ[R[TZUYWV',
    'j': '  660 20PWSMSNTNTMSM RPVRRLdKfIgHfHdIaL^O\Q[TYWV',
    'k': '  661 33M[MVOSRNSLTITGSFQGPIOMNSM[ RM[NXOVQSSRURVSVUTVQV RQVSWTZU[V[XZYY[V',
    'l': '  662 18OWOVQSTNULVIVGUFSGRIQMPTPZQ[R[TZUYWV',
    'm': '  663 33E^EVGSIRJSJTIXH[ RIXJVLSNRPRQSQTPXO[ RPXQVSSURWRXSXUWXWZX[Y[[Z\Y^V',
    'n': '  664 23J\JVLSNROSOTNXM[ RNXOVQSSRURVSVUUXUZV[W[YZZY\V',
    'o': '  665 23LZRRPRNSMTLVLXMZO[Q[SZTYUWUUTSRRQSQURWTXWXYWZV',
    'p': '  666 24KZKVMSNQMUGg RMUNSPRRRTSUUUWTYSZQ[ RMZO[R[UZWYZV',
    'q': '  667 27L[UUTSRRPRNSMTLVLXMZO[Q[SZ RVRUUSZPaOdOfPgRfScS\\U[XY[V',
    'r': '  668 15MZMVOSPQPSSSTTTVSYSZT[U[WZXYZV',
    's': '  669 16NYNVPSQQQSSVTXTZR[ RNZP[T[VZWYYV',
    't': '  670 16OXOVQSSO RVFPXPZQ[S[UZVYXV RPNWN',
    'u': '  671 19L[LVNRLXLZM[O[QZSXUU RVRTXTZU[V[XZYY[V',
    'v': '  672 17L[LVNRMWMZN[O[RZTXUUUR RURVVWWYW[V',
    'w': '  673 25I^LRJTIWIYJ[L[NZPX RRRPXPZQ[S[UZWXXUXR RXRYVZW\W^V',
    'x': '  674 20JZJVLSNRPRQSQZR[U[XYZV RWSVRTRSSOZN[L[KZ',
    'y': '  675 23L[LVNRLXLZM[O[QZSXUU RVRPdOfMgLfLdMaP^S\\U[XY[V',
    'z': '  676 23LZLVNSPRRRTTTVSXQZN[P\Q^QaPdOfMgLfLdMaP^S\\WYZV',

    '0': '  700 18H\\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF',
    '1': '  701  5H\\NJPISFS[',
    '2': '  702 15H\\LKLJMHNGPFTFVGWHXJXLWNUQK[Y[',
    '3': '  703 16H\\MFXFRNUNWOXPYSYUXXVZS[P[MZLYKW',
    '4': '  704  7H\\UFKTZT RUFU[',
    '5': '  705 18H\\WFMFLOMNPMSMVNXPYSYUXXVZS[P[MZLYKW',
    '6': '  706 24H\\XIWGTFRFOGMJLOLTMXOZR[S[VZXXYUYTXQVOSNRNOOMQLT',
    '7': '  707  6H\\YFO[ RKFYF',
    '8': '  708 30H\\PFMGLILKMMONSOVPXRYTYWXYWZT[P[MZLYKWKTLRNPQOUNWMXKXIWGTFPF',
    '9': '  709 24H\\XMWPURRSQSNRLPKMKLLINGQFRFUGWIXMXRWWUZR[P[MZLX'
    }

type_glyps = {
    'A': r' 2001 18H\RFK[ RRFY[ RRIX[ RMUVU RI[O[ RU[[[',
    'B': r' 2002 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUP RUFWGXHYJYLXNWOUP RMPUPXQYRZTZWYYXZU[I[ RUPWQXRYTYWXYWZU[',
    'C': r' 2003 32G\XIYLYFXIVGSFQFNGLIKKJNJSKVLXNZQ[S[VZXXYV RQFOGMILKKNKSLVMXOZQ[',
    'D': r' 2004 30G]LFL[ RMFM[ RIFSFVGXIYKZNZSYVXXVZS[I[ RSFUGWIXKYNYSXVWXUZS[',
    'E': r' 2005 22G\LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[Y[YUX[',
    'F': r' 2006 20G[LFL[ RMFM[ RSLST RIFYFYLXF RMPSP RI[P[',
    'G': r' 2007 40G^XIYLYFXIVGSFQFNGLIKKJNJSKVLXNZQ[S[VZXX RQFOGMILKKNKSLVMXOZQ[ RXSX[ RYSY[ RUS\S',
    'H': r' 2008 27F^KFK[ RLFL[ RXFX[ RYFY[ RHFOF RUF\F RLPXP RH[O[ RU[\[',
    'I': r' 2009 12MXRFR[ RSFS[ ROFVF RO[V[',
    'J': r' 2010 20KZUFUWTZR[P[NZMXMVNUOVNW RTFTWSZR[ RQFXF',
    'K': r' 2011 27F\KFK[ RLFL[ RYFLS RQOY[ RPOX[ RHFOF RUF[F RH[O[ RU[[[',
    'L': r' 2012 14I[NFN[ ROFO[ RKFRF RK[Z[ZUY[',
    'M': r' 2013 30F_KFK[ RLFRX RKFR[ RYFR[ RYFY[ RZFZ[ RHFLF RYF]F RH[N[ RV[][',
    'N': r' 2014 21G^LFL[ RMFYY RMHY[ RYFY[ RIFMF RVF\F RI[O[',
    'O': r' 2015 44G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF',
    'P': r' 2016 29G]LFL[ RMFM[ RIFUFXGYHZJZMYOXPUQMQ RUFWGXHYJYMXOWPUQ RI[P[',
    'Q': r' 2017 64G]QFNGLIKKJOJRKVLXNZQ[S[VZXXYVZRZOYKXIVGSFQF RQFOGMILKKOKRLVMXOZQ[ RS[UZWXXVYRYOXKWIUGSF RNYNXOVQURUTVUXV_W`Y`Z^Z] RUXV\W^X_Y_Z^',
    'R': r' 2018 45G]LFL[ RMFM[ RIFUFXGYHZJZLYNXOUPMP RUFWGXHYJYLXNWOUP RI[P[ RRPTQURXYYZZZ[Y RTQUSWZX[Z[[Y[X',
    'S': r' 2019 34H\XIYFYLXIVGSFPFMGKIKKLMMNOOUQWRYT RKKMMONUPWQXRYTYXWZT[Q[NZLXKUK[LX',
    'T': r' 2020 16I\RFR[ RSFS[ RLFKLKFZFZLYF RO[V[',
    'U': r' 2021 23F^KFKULXNZQ[S[VZXXYUYF RLFLUMXOZQ[ RHFOF RVF\F',
    'V': r' 2022 15H\KFR[ RLFRX RYFR[ RIFOF RUF[F',
    'W': r' 2023 24F^JFN[ RKFNV RRFN[ RRFV[ RSFVV RZFV[ RGFNF RWF]F',
    'X': r' 2024 21H\KFX[ RLFY[ RYFK[ RIFOF RUF[F RI[O[ RU[[[',
    'Y': r' 2025 20H]KFRQR[ RLFSQS[ RZFSQ RIFOF RVF\F RO[V[',
    'Z': r' 2026 16H\XFK[ RYFL[ RLFKLKFYF RK[Y[YUX[',

    'a': r' 2101 39I]NONPMPMONNPMTMVNWOXQXXYZZ[ RWOWXXZZ[[[ RWQVRPSMTLVLXMZP[S[UZWX RPSNTMVMXNZP[',
    'b': r' 2102 33G\LFL[ RMFM[ RMPONQMSMVNXPYSYUXXVZS[Q[OZMX RSMUNWPXSXUWXUZS[ RIFMF',
    'c': r' 2103 28H[WPVQWRXQXPVNTMQMNNLPKSKULXNZQ[S[VZXX RQMONMPLSLUMXOZQ[',
    'd': r' 2104 36H]WFW[ RXFX[ RWPUNSMQMNNLPKSKULXNZQ[S[UZWX RQMONMPLSLUMXOZQ[ RTFXF RW[[[',
    'e': r' 2105 31H[LSXSXQWOVNTMQMNNLPKSKULXNZQ[S[VZXX RWSWPVN RQMONMPLSLUMXOZQ[',
    'f': r' 2106 22KXUGTHUIVHVGUFSFQGPIP[ RSFRGQIQ[ RMMUM RM[T[',
    'g': r' 2107 60I\QMONNOMQMSNUOVQWSWUVVUWSWQVOUNSMQM RONNPNTOV RUVVTVPUN RVOWNYMYNWN RNUMVLXLYM[P\U\X]Y^ RLYMZP[U[X\Y^Y_XaUbObLaK_K^L\O[',
    'h': r' 2108 28G]LFL[ RMFM[ RMPONRMTMWNXPX[ RTMVNWPW[ RIFMF RI[P[ RT[[[',
    'i': r' 2109 18MXRFQGRHSGRF RRMR[ RSMS[ ROMSM RO[V[',
    'j': r' 2110 25MXSFRGSHTGSF RTMT_SaQbObNaN`O_P`Oa RSMS_RaQb RPMTM',
    'k': r' 2111 27G\LFL[ RMFM[ RWMMW RRSX[ RQSW[ RIFMF RTMZM RI[P[ RT[Z[',
    'l': r' 2112 12MXRFR[ RSFS[ ROFSF RO[V[',
    'm': r' 2113 44BcGMG[ RHMH[ RHPJNMMOMRNSPS[ ROMQNRPR[ RSPUNXMZM]N^P^[ RZM\N]P][ RDMHM RD[K[ RO[V[ RZ[a[',
    'n': r' 2114 28G]LML[ RMMM[ RMPONRMTMWNXPX[ RTMVNWPW[ RIMMM RI[P[ RT[[[',
    'o': r' 2115 36H\QMNNLPKSKULXNZQ[S[VZXXYUYSXPVNSMQM RQMONMPLSLUMXOZQ[ RS[UZWXXUXSWPUNSM',
    'p': r' 2116 36G\LMLb RMMMb RMPONQMSMVNXPYSYUXXVZS[Q[OZMX RSMUNWPXSXUWXUZS[ RIMMM RIbPb',
    'q': r' 2117 33H\WMWb RXMXb RWPUNSMQMNNLPKSKULXNZQ[S[UZWX RQMONMPLSLUMXOZQ[ RTb[b',
    'r': r' 2118 23IZNMN[ ROMO[ ROSPPRNTMWMXNXOWPVOWN RKMOM RK[R[',
    's': r' 2119 32J[WOXMXQWOVNTMPMNNMOMQNRPSUUWVXW RMPNQPRUTWUXVXYWZU[Q[OZNYMWM[NY,',
    't': r' 2120 16KZPFPWQZS[U[WZXX RQFQWRZS[ RMMUM',
    'u': r' 2121 28G]LMLXMZP[R[UZWX RMMMXNZP[ RWMW[ RXMX[ RIMMM RTMXM RW[[[',
    'v': r' 2122 15I[LMR[ RMMRY RXMR[ RJMPM RTMZM',
    'w': r' 2123 24F^JMN[ RKMNX RRMN[ RRMV[ RSMVX RZMV[ RGMNM RWM]M',
    'x': r' 2124 21H\LMW[ RMMX[ RXML[ RJMPM RTMZM RJ[P[ RT[Z[',
    'y': r' 2125 22H[LMR[ RMMRY RXMR[P_NaLbKbJaK`La RJMPM RTMZM',
    'z': r' 2126 16I[WML[ RXMM[ RMMLQLMXM RL[X[XWW[',

    '0': r' 2200 40H\QFNGLJKOKRLWNZQ[S[VZXWYRYOXJVGSFQF RQFOGNHMJLOLRMWNYOZQ[ RS[UZVYWWXRXOWJVHUGSF',
    '1': r' 2201 11H\NJPISFS[ RRGR[ RN[W[',
    '2': r' 2202 45H\LJMKLLKKKJLHMGPFTFWGXHYJYLXNUPPRNSLUKXK[ RTFVGWHXJXLWNTPPR RKYLXNXSZVZXYYX RNXS[W[XZYXYV',
    '3': r' 2203 47H\LJMKLLKKKJLHMGPFTFWGXIXLWNTOQO RTFVGWIWLVNTO RTOVPXRYTYWXYWZT[P[MZLYKWKVLUMVLW RWQXTXWWYVZT[',
    '4': r' 2204 13H\THT[ RUFU[ RUFJUZU RQ[X[',
    '5': r' 2205 39H\MFKP RKPMNPMSMVNXPYSYUXXVZS[P[MZLYKWKVLUMVLW RSMUNWPXSXUWXUZS[ RMFWF RMGRGWF',
    '6': r' 2206 48H\WIVJWKXJXIWGUFRFOGMILKKOKULXNZQ[S[VZXXYUYTXQVOSNRNOOMQLT RRFPGNIMKLOLUMXOZQ[ RS[UZWXXUXTWQUOSN',
    '7': r' 2207 31H\KFKL RKJLHNFPFUIWIXHYF RLHNGPGUI RYFYIXLTQSSRVR[ RXLSQRSQVQ[',
    '8': r' 2208 63H\PFMGLILLMNPOTOWNXLXIWGTFPF RPFNGMIMLNNPO RTOVNWLWIVGTF RPOMPLQKSKWLYMZP[T[WZXYYWYSXQWPTO RPONPMQLSLWMYNZP[ RT[VZWYXWXSWQVPTO',
    '9': r' 2209 48H\XMWPURRSQSNRLPKMKLLINGQFSFVGXIYLYRXVWXUZR[O[MZLXLWMVNWMX RQSORMPLMLLMIOGQF RSFUGWIXLXRWVVXTZR['
}

my_line_us = LineUs('line-us.local')

print(my_line_us.get_hello_string())
time.sleep(1)
my_line_us.home()

# I've fiddled with the aspect ratio of the 
# font to make it look good on the line-us
#
l_aspect_radio = 1.25
l_scale = 8
l_x_base = 100
l_y_base = 100

x = 0
y = 0

while True:
    output_type = input("Sript (S) or Typed (T) text:")
    if output_type.upper() == 'S':
        glyphs = script_glyphs
        break
    if output_type.upper() == 'T':
        glyphs = type_glyps
        break
    
input_text = input("What do you want to print:")

for c in input_text:

    if c == "_":
        # Take a new line
        x=0
        y = y + 25
        continue

    if c==' ':
        # insert an i space
        glyph = hersheyparse(glyphs['i'])
    else:
        glyph = hersheyparse(glyphs[c])
        for line in glyph['lines']:
            first = 1
            for pt in line:
                rx = x + pt[0] - glyph['left']
                ry = y + pt[1]
                lx = l_y_base + (l_scale * l_aspect_radio * ry)
                ly = l_x_base + (l_scale * rx)
                if first == 1:
                    first = 0
                    my_line_us.move(lx,ly)
                else:
                    my_line_us.draw(lx,ly)
    x = x + (glyph['right'] - glyph['left'])

time.sleep(1)
my_line_us.disconnect()

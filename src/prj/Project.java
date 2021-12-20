package prj;

import javacard.framework.APDU;
import javacard.framework.Applet;
import javacard.framework.ISO7816;
import javacard.framework.ISOException;
import javacard.framework.Util;
import javacard.framework.JCSystem;
import javacard.security.RandomData;
import javacard.security.KeyBuilder;
import javacard.security.Signature;
import javacard.security.KeyPair;
import javacard.security.PublicKey;
import javacard.security.PrivateKey;
import javacard.security.CryptoException;
import javacard.security.RSAPrivateCrtKey;
import javacard.security.RSAPublicKey;


import javacard.framework.*;
import javacard.security.*;


import java.lang.SecurityException;
import java.lang.RuntimeException;

public class Project extends Applet {

    public static final byte CLA_MONAPPLET = (byte) 0xA0;

    public static final byte INS_INSERT_PIN = (byte) 0x00;
    public static final byte INS_INSERT_PIN_FESTIVAL = (byte) 0x01;
    public static final byte INS_MODIFY_MONEY = (byte) 0x02;
    public static final byte INS_SEND_ID = (byte) 0x03;
    public static final byte INS_SHARE_PK_MOD = (byte) 0x06;
    public static final byte INS_SHARE_PK_EXP = (byte) 0x07;
    public static final byte INS_VERIFY_PK = (byte) 0x08;
    public static final byte INS_STATUS_MONEY = (byte) 0x09;
    public static final byte INS_SIGN_STATUS = (byte) 0x0A;
    public static final byte INS_WRITE_INFO = (byte) 0x0B;
    public static final byte INS_SEND_INFO = (byte) 0x0C;
    public static final byte INS_SIGN_INFO = (byte) 0x0D;
    
    private static OwnerPIN PIN;
    private static OwnerPIN PIN_FESTIVAL;
    private static byte [] ID;
    private static byte [] info;
    
    private static byte [] pin_ins;
    private static short MAX_LENGTH_PIN = (short)4;
    private static short MAX_LENGTH_KEY = (short)256;  //specified in key pair construction
    private static short MAX_LENGTH_ID = (short)4;

    private short MAX_LENGTH_MONEY = (short)2;
    private short MAX_MONEY = (short)65000;
    
    private static byte max_tries = (byte)3;

    private  Signature sig;
    private  KeyPair key_pair;
    private  RSAPublicKey pk;
    private  RSAPrivateCrtKey vk;
    private  short ln = 0;
    private  byte[] publicKeyModulus = new byte[MAX_LENGTH_KEY];
    private  byte[] publicKeyExponent = new byte[MAX_LENGTH_KEY];
    private  short exp_len;

    private  byte[] wallet = new byte[MAX_LENGTH_MONEY]; //money on card

    private  boolean retrieve_mod_pk_card = true;
    private  boolean retrieve_exp_pk_card = true;

    private short ERROR = (short) 0xFACE;
    
    /*Constructor*/
    private Project(byte bArray[], short bOffset, byte bLength) {
	register();

	byte aidLength = bArray[bOffset];
	byte controlLength = bArray[(short)(bOffset+1+aidLength)];
	byte dataLength = bArray[(short)(bOffset+1+aidLength+1+controlLength)];

	short dataOffset = (short)(bOffset+1+aidLength+1+controlLength+1);
	pin_ins = JCSystem.makeTransientByteArray(MAX_LENGTH_PIN, JCSystem.CLEAR_ON_RESET);
	PIN = new OwnerPIN(max_tries, (byte) MAX_LENGTH_PIN);
	PIN.update(bArray, dataOffset, (byte) MAX_LENGTH_PIN);
	ID = new byte[MAX_LENGTH_ID];
	Util.arrayCopy(bArray,(short)(dataOffset+MAX_LENGTH_PIN), ID, (short) 0,MAX_LENGTH_ID);
	PIN_FESTIVAL = new OwnerPIN(max_tries, (byte) MAX_LENGTH_PIN);
	PIN_FESTIVAL.update(bArray, (short)(dataOffset+MAX_LENGTH_ID+MAX_LENGTH_PIN), (byte) MAX_LENGTH_PIN);


        try {
	    sig = Signature.getInstance(Signature.ALG_RSA_SHA_PKCS1, false);
	    key_pair = new KeyPair(KeyPair.ALG_RSA_CRT, KeyBuilder.LENGTH_RSA_2048);
	    key_pair.genKeyPair();
	    pk = (RSAPublicKey) key_pair.getPublic();
	    vk = (RSAPrivateCrtKey) key_pair.getPrivate();
	    pk.getModulus(publicKeyModulus, (short) 0);
	    exp_len = pk.getExponent(publicKeyExponent, (short) 0);
	} catch (CryptoException c) {
	    short reason = c.getReason();
	    ISOException.throwIt(reason);
	}

        
    }

        
    public static void install(byte bArray[], short bOffset, byte bLength) throws ISOException {

	if(bLength == 0)
	   ISOException.throwIt(ISO7816.SW_FUNC_NOT_SUPPORTED);
	new Project(bArray, bOffset, bLength);
        
    }

    public void process(APDU apdu) throws ISOException{

	byte [] buffer = apdu.getBuffer();
	short lc;
	boolean equal, check;
	byte [] ret;
	byte [] tmp;
	short sum, cnt;
	short l;

	if (this.selectingApplet())   return;

	if (buffer[ISO7816.OFFSET_CLA] != CLA_MONAPPLET) {
	    ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
	}

	switch(buffer[ISO7816.OFFSET_INS]) {


	    case INS_SEND_ID:

		apdu.setIncomingAndReceive();

		lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

	        Util.arrayCopyNonAtomic(ID,
					(short)0,
					buffer,
					ISO7816.OFFSET_CDATA,
					MAX_LENGTH_ID);
		apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, MAX_LENGTH_ID);

		break;

            case INS_SHARE_PK_MOD:

		if (retrieve_mod_pk_card == true){

		    retrieve_mod_pk_card = false;
		    
		    Util.arrayCopyNonAtomic(publicKeyModulus,
					    (short)0,
					    buffer,
					    ISO7816.OFFSET_CDATA,
					    MAX_LENGTH_KEY);
		    apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA,MAX_LENGTH_KEY);
		}else{
		    ISOException.throwIt(ERROR);
		}
		break;
		
	    case INS_SHARE_PK_EXP:
		
	       
		if (retrieve_exp_pk_card == true){

		    retrieve_exp_pk_card = false;
		    Util.arrayCopyNonAtomic(publicKeyExponent,
					    (short)0,
					    buffer,
					    ISO7816.OFFSET_CDATA,
					    exp_len);
		    apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA,exp_len);
		}else{
		    ISOException.throwIt(ERROR);
		}
		break;

        

	    case INS_VERIFY_PK:

		
		
		apdu.setIncomingAndReceive();

		lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

		byte [] chall = new byte[lc];
		
		Util.arrayCopyNonAtomic(buffer,
					ISO7816.OFFSET_CDATA,
					chall,
					(short)0,
					lc);

		try {
		    sig.init(vk, Signature.MODE_SIGN);

		    l = sig.sign(chall,(short) 0, (short)chall.length, buffer,  ISO7816.OFFSET_CDATA);
	            apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, l);
       		 } catch (CryptoException c) {
            	   short reason = c.getReason();
        	    ISOException.throwIt(reason);
	        }

		break;

		
	    case INS_INSERT_PIN:

	    
	        lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

	    
		apdu.setIncomingAndReceive();

		Util.arrayCopyNonAtomic(buffer,
					ISO7816.OFFSET_CDATA,
					pin_ins,
					(short)0,
					lc);

		check = PIN.check(pin_ins,(short)0,(byte)lc);

	        ret = new byte[2];
		if(check == true){
			ret[1]=0x1;
		}else{
                        ret[1]=0x0;
			ret[0]=PIN.getTriesRemaining();
                }

		Util.arrayCopyNonAtomic(ret,
                                        (short)0,
                                        buffer,
                                        ISO7816.OFFSET_CDATA,
                                        (short)2);
                apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, (short)2);

		break;

	    case INS_INSERT_PIN_FESTIVAL:

	    
	        lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

	    
		apdu.setIncomingAndReceive();

		Util.arrayCopyNonAtomic(buffer,
					ISO7816.OFFSET_CDATA,
					pin_ins,
					(short)0,
					lc);

		check = PIN_FESTIVAL.check(pin_ins,(short)0,(byte)lc);

	        ret = new byte[2];
		if(check == true){
			ret[1]=0x1;
		}else{
                        ret[1]=0x0;
			ret[0]=PIN_FESTIVAL.getTriesRemaining();
                }

		Util.arrayCopyNonAtomic(ret,
                                        (short)0,
                                        buffer,
                                        ISO7816.OFFSET_CDATA,
                                        (short)2);
                apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, (short)2);

		break;



	    case INS_MODIFY_MONEY:

		lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

	        
		tmp = new byte[MAX_LENGTH_MONEY];
		if(!PIN.isValidated() || !PIN_FESTIVAL.isValidated() || lc != MAX_LENGTH_MONEY){
		    ISOException.throwIt(ERROR);
		}
		    
		
		apdu.setIncomingAndReceive();
		
		Util.arrayCopyNonAtomic(buffer,
				    ISO7816.OFFSET_CDATA,
				    tmp,
				    (short)0,
				    lc);

	        for(short i=0;i<MAX_LENGTH_MONEY;i++){
		    wallet[i] = tmp[i];
		}
	        
	        

		
		break;

	    case INS_STATUS_MONEY:

	        if(!PIN.isValidated() || !PIN_FESTIVAL.isValidated()){
		    ISOException.throwIt(ERROR);
		}
	        
		Util.arrayCopyNonAtomic(wallet,
					(short)0,
					buffer,
					ISO7816.OFFSET_CDATA,
					MAX_LENGTH_MONEY);
		
		apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, MAX_LENGTH_MONEY);	
	                

		break;

	    case INS_SIGN_STATUS:

		if(!PIN.isValidated() || !PIN_FESTIVAL.isValidated()){
		    ISOException.throwIt(ERROR);
		}
		
		try {
		    sig.init(vk, Signature.MODE_SIGN);

		    l = sig.sign(wallet,(short) 0, MAX_LENGTH_MONEY, buffer, (short)ISO7816.OFFSET_CDATA);
	            apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, l);
       		 } catch (CryptoException c) {
            	   short reason = c.getReason();
        	    ISOException.throwIt(reason);
	        }
		
		break;

	    case INS_WRITE_INFO:

		if(!PIN.isValidated() || !PIN_FESTIVAL.isValidated()){
		    ISOException.throwIt(ERROR);
		}

		apdu.setIncomingAndReceive();

		lc = (short)(buffer[ISO7816.OFFSET_LC] & 0xff); //APDU sends other info in the other bytes -- as lc can be 1 or 3 bytes long

		info = new byte[lc];

		
		Util.arrayCopyNonAtomic(buffer,
					ISO7816.OFFSET_CDATA,
					info,
					(short)0,
					lc);

		
		break;

	    case INS_SEND_INFO:

		
		Util.arrayCopyNonAtomic(info,
				        (short)0,
					buffer,
				        ISO7816.OFFSET_CDATA,
					(short)info.length);

		apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA,(short)(info.length));
		
		break;

	    case INS_SIGN_INFO:

		try {
		    sig.init(vk, Signature.MODE_SIGN);

		    l = sig.sign(info,(short) 0, (short)info.length, buffer, (short)ISO7816.OFFSET_CDATA);
	            apdu.setOutgoingAndSend(ISO7816.OFFSET_CDATA, l);
       		 } catch (CryptoException c) {
            	   short reason = c.getReason();
        	    ISOException.throwIt(reason);
	        }
		
		break;
		
	}
	
    }
    
}



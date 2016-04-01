#!/usr/bin/perl -W
# funzioni usate dai script perl
package funzioni;

use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;
use CGI::Session;
use XML::LibXML;
use Fcntl qw(:flock :DEFAULT);

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#subruotine per la stampa dell'html

sub printHead {
#stampa html head e body (fino al javascript), richiede "titolo" e si possono aggiungere keywords
  my $param=shift;
  my $keywords;
  if(exists $param->{keywords}) { $keywords=','.$param->{keywords}; }
  print <<EOHEAD;
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="it" lang="it">
<head><script type="text/javascript" src="../script.js"></script>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
EOHEAD

  if($param->{titolo}) { print "<title>CucinaFelice - $param->{titolo}</title>"; }
  else { print '<title>CucinaFelice</title>'; }
  print <<EOHEAD1;
<meta name="description" content="ricette di tutti i tipi" />
<meta name="keywords" content="ricette,cibo,antipasti,primi,secondi,dolci,aperitivi$keywords" />
<meta name="author" content="Viviana Alessio, Giuseppe Merlino, Miki Violetto" />
<meta name="language" content="italian it" />
<link type="text/css" rel="stylesheet" href="../css/base.css" media="screen" />
<link type="text/css" rel="stylesheet" href="../css/aural.css" media="aural" />
<meta content="width=device-width, initial-scale=1.0, maximum-scale=10.0, user-scalable=yes" name="viewport" id="layout" />
<link type="text/css" rel="stylesheet" href="../css/print.css" media="print" />
<link rel="icon" href="../immagini/favicon.png" type="image/x-icon" />
</head><body onload="zoomdisabler()">
<div id="header">
<a class="logo" accesskey="h" href="home.cgi">
<img src="../immagini/titolo1.png" alt="logo del sito cucinafelice, clicca per tornare alla home page o utilizza l'accesskey alt+h" /></a>
EOHEAD1

}

sub printModuloLogin {
#stampa la form per il login, richiede $user,$indirizzo,$array{stato} e altri dipendenti dai casi
  my $param=shift;
  #box loggato
  if(exists $param->{user}) {
    print '<div id="login"><form><p>Ciao '.$param->{user}.'</p>';
    print '<input type="button" onClick="location.href=\''.cambiaGet($param->{indirizzo}).'action=logout\'" class="buttonlogged" name="logout" value="Esci" />';
    unless(exists $param->{area}) {
      print '<input type="button" onClick="location.href=\'area-personale.cgi\'" class="buttonlogged" value="Area privata" />';
    }
    print '</p></form></div>';
  }
  else {
  #box con form login
    print '<div id="login"><span class="hide"><a href="#path">Salta la form di login</a></span><form method="post" action="'.$param->{indirizzo}.'"><h3>Login: ';
    if($param->{errore}) { print 'Credenziali sbagliate'; }
    print <<EOLOGIN;
</h3><p><label class="loginleft" for="username">Inserisci Username</label>
<input class="loginright" type="text" name="username" id="username" value="$param->{username}" /></p><p>
<label class="loginleft" for="password">Inserisci Password</label>
<input class="loginright" type="password" name="password" id="password" value="$param->{password}" /></p><p>
<a class="loginleft" href="recupera.cgi">Recupera Dati</a>
<input type="submit" name="action" class="button" value="login" />
<a href="registrazione.cgi"><input type="button" name="register" class="button" id="register" value="Registrati" /></a></p></form></div>
EOLOGIN

  }
}

sub printPathNav {
#stampa il path e il nav, richiede $param{dove} per il path e $param{nascondi} per poter rimuovere il link che non serve
  my $param=shift;
  print '</div><div id="path">Ti trovi in ';
  if(exists $param->{nascondip}) {
    print '<a href="home.cgi"><span xml:lang="en">Home</span></a>';
    $param->{nascondi}=$param->{nascondip};
  }
  elsif($param->{nascondi} eq 'home') { print '<span xml:lang="en">Home</span>'; }
  else { print '<a href="home.cgi"><span xml:lang="en">Home</span></a>'; }
  if($param->{dove}) { print ' &gt; '.ucfirst $param->{dove}; }
  print '</div><div id="nav"><span class="hide"><a href="#corpo">Salta il menu di navigazione</a></span><ul><li>';
  if($param->{nascondi} eq 'all') { print 'Tutte le ricette</li><li>'; }
  else { print '<a href="ricettario.cgi">Tutte le ricette</a></li><li>'; }
  if($param->{nascondi} eq 'aperitivi') { print 'Aperitivi</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=aperitivi">Aperitivi</a></li><li>'; }
  if($param->{nascondi} eq 'antipasti') { print 'Antipasti</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=antipasti">Antipasti</a></li><li>'; }
  if($param->{nascondi} eq 'primi') { print 'Primi</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=primi">Primi</a></li><li>'; }
  if($param->{nascondi} eq 'secondi') { print 'Secondi</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=secondi">Secondi</a></li><li>'; }
  if($param->{nascondi} eq 'contorni') { print 'Contorni</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=contorni">Contorni</a></li><li>'; }
  if($param->{nascondi} eq 'dolci') { print 'Dolci</li><li>'; }
  else { print '<a href="ricettario.cgi?tipo=dolci">Dolci</a></li>'; }
  print '</ul></div><div id="corpo"> ';
}
sub printAncora {
#stampa l'ancora a fine pagina
  print '<a id="su" href="#top">Torna a inizio pagina</a>';
}

sub printFoot {
#stampa il foot,richiede $indirizzo
  my $indirizzo=shift;
  print <<EOFOOT;
</div><div id="foot">
<a href="http://validator.w3.org/check?uri=http://tecnologie-web.studenti.math.unipd.it/tecweb/~mviolett/cgi-bin/$indirizzo">
<img src="http://www.w3.org/Icons/valid-xhtml10" alt="XHTML 1.0 Strict Valido!" />
</a>&#169;The C-TEAM corporation<a href="http://jigsaw.w3.org/css-validator/check?uri=http://tecnologie-web.studenti.math.unipd.it/tecweb/~mviolett/cgi-bin/$indirizzo">
<img src="http://jigsaw.w3.org/css-validator/images/vcss" alt="CSS Valido!" /></a></div></body></html>
EOFOOT

}

sub printCommento {
#stampa un commento
  my $param=shift;
  my $nodocommento=$param->{nodo};
  my $indirizzo=$param->{indirizzo};
  
  my $id=$nodocommento->getAttribute('id');
  my $utente=$nodocommento->findvalue('utente');
  my $abil;
  if($nodocommento->exists('abilita')) { $abil=$nodocommento->findvalue('abilita'); }
  my $voto;
  if($nodocommento->exists('voto')) { $voto=$nodocommento->findvalue('voto'); }
  my $testo=$nodocommento->findnodes('testo/text()')->get_node(1)->toString('UTF-8',1);
  my $data=&cambiaData($nodocommento->findvalue('data'));
  my $segnalato;
  if($nodocommento->hasAttribute('segnalato')) { $segnalato='si'; }
  #stampo l'html del commento
  print '<div class="commento"><div class="int_commento"><p class="autore"> Autore: <span>'.$utente.'</span>';
  if($abil) { print ' Abiità: <span>'.$abil.'</span>'; }
  print '</p><p class="data">'.$data.'</p></div><div class="testo_commento">'.$testo.'</div>';
  if($voto) { print '<p>Voto: <span>'.$voto.'</span></p>'; }
  print '<div class="bottoni">';
  if($segnalato) {
    if($param->{admin} eq 'true') { print '<p><input type="button" class="button" onClick="location.href=\''.funzioni::cambiaGet( $indirizzo ).'togli='.$id.'\'" value="togli" /></p>'; }
    else { print '<p>segnalato e in attesa di verifica</p>'; }
  }
  else {
    if($param->{user}) { print '<p><input type="button" class="button" onClick="location.href=\''.funzioni::cambiaGet( $indirizzo ).'segnala='.$id.'\'" value="segnala" /></p>'; }
  }
  if($param->{admin} eq 'true' or ($param->{user} eq $utente)) { print '<p><input type="button" class="button" onClick="location.href=\''.funzioni::cambiaGet( $indirizzo ).'rimuovi='.$id.'\'" value="rimuovi" /></p>'; }
  print '</div></div>';
}

sub previewImmagine {
#stampa un'immagine
  my $nodoimmagine=shift;
  my $immagine=$nodoimmagine->toString('UTF-8',1);
  $immagine=~s/<img><url>/<img class="preview" src="..\//g;
  $immagine=~s/<\/url><alt>/\" alt=\"/g;
  $immagine=~s/<\/alt><\/img>/\" \/>/g;
  return $immagine;
}
#####################################################################################################################################################
#funzioni meno legate all'html

sub checkSession {
#fa tutto il lavoro iniziale
  #inizializzazioni variabili utili
  my $indirizzoxmlutenti='../data/utenti.xml';
  my $action=shift;
  my $session;
  my $CGISESSID;
  my %array; $array{stato}=0; $array{descrizione};
  
  my %cookies=CGI::Cookie->fetch;
  if(exists $cookies{CGISESSID} and $cookies{CGISESSID}->value() ne '') {
  #se esiste allora "sono loggato" (sempre se la sessione c'è ancora..) 
    $CGISESSID=$cookies{CGISESSID}->value();
    $session= CGI::Session->load(undef,$CGISESSID);
    if(!$session or $session->is_empty or $session->is_expired) {
    #non ho la sessione, deve riloggarsi
      $array{errore}=1;
      $array{descrizione}='no session find';
    } else {
    #ho la sessione
      $array{descrizione}='session find';
      #controllo se devo fare il logout
      if($action eq 'logout') {
	#cancello il cookie
	my $cookie=CGI::Cookie->new(-name=>'CGISESSID',-value=>'');
	print "Set-Cookie: $cookie\n";
	#cancello la sessione
	$session->close();
	$session->delete();
	$session->flush();
	#ritorno 
	$array{errore}=-1;
	$array{descrizione}.=' , logout effettuato';
	print "Content-type: text/html\n\n";
	return %array;
      }
      #modifico la durata della sessione e del cookie
      my $cookie=CGI::Cookie->new(-name=>'CGISESSID',-value=>$session->id,-expires => '2h');
      $array{stato}=1;
      $array{session}=$session;
      print "Set-Cookie: $cookie\n";
      print "Content-type: text/html\n\n";
      $session->flush();
      return %array;
    }
  } else {
  #non esiste il cookie, o esiste ma è vuoto a seguito del logout
    $array{errore}=2;
    $array{descrizione}='no cookie find';
  }
  #se non ho caricato la sessione potrei avere i dati della form per loggarmi
  if(exists $array{errore}) {
  #controllo se sono arrivato tramite la form del login
    my %form; my $buffer;
    #recupero i dati inviati tramite metodo post
    read(STDIN,$buffer,$ENV{'CONTENT_LENGTH'});
    my @pairs=split(/&/,$buffer);
    foreach my $pair (@pairs) {
      my ($name,$value)=split(/=/,$pair);
      $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
      $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
      $form{$name}=$value;
    }
    #controllo se sono arrivato tramite form del login
    if($form{action} ne 'login') {
    #non sono arrivato tramite la form e prima non avevo trovato la sessione
      $array{errore}=$array{errore}+2;
      $array{descrizione}.=' , no submit form';
      print "Content-type: text/html\n\n";
      return %array;
    }
    #ho la form, provo a loggarmi
    $array{descrizione}.=' , submit form';
    #ricontrollo la validità dei dati inviati
    if ($form{username}!~/[a-zA-Z0-9]{2,}/) {
    #errore sull'username
      $array{errore}=$array{errore}+4;
      $array{login}=1;
      $array{descrizione}.=' : wrong pattern username';
      print "Content-type: text/html\n\n";
      return %array;
    } 
    if ($form{password}!~/[a-zA-Z0-9]{8,20}/) {
    #errore sulla password
      $array{errore}=$array{errore}+6;
      $array{login}=2;
      $array{descrizione}.=' : wrong pattern password';
      print "Content-type: text/html\n\n";
      return %array;
    }
  
    #dopo aver validato username e password controllo se esiste l'username, e in tal caso se la password combacia
    open (*UTENTI,$indirizzoxmlutenti);
    flock (*UTENTI,1);
    my $xmlutenti=XML::LibXML->load_xml({IO=>*UTENTI});
    close (*UTENTI); # si occupa lui di flock 8
    unless($xmlutenti->exists("//utente[username=\'$form{username}\']") and $xmlutenti->findvalue("//utente[username=\'$form{username}\']/password") eq $form{password}) {
      $array{errore}=$array{errore}+8;
      $array{descrizione}.=' : wrong username or password';
      $array{login}=3;
      $array{username}=$form{username};
      $array{password}=$form{password};
      print "Content-type: text/html\n\n";
      return %array;
    }
    #login valida, creo sessione e cookie
    $session= CGI::Session->new();
    $session->expire('2h');
    $session->param('utente',$form{username});
    #controllo se l'utente è admin
    my $admin=$xmlutenti->findvalue("//utente/\@admin[../username=\'$form{username}\']");
    $session->param('admin',$admin);
    #controllo se l'utente ha inserito l'abilità
    if($xmlutenti->exists("//utente[username=\'$form{username}\']/infoaggiuntive/abilita")) {
      $session->param('abilita',$xmlutenti->findvalue("//utente[username=\'$form{username}\']/infoaggiuntive/abilita")); }
    #sincronizzo i dati
    $session->flush();
    #modifico il cookie
    my $cookie=CGI::Cookie->new(-name=>'CGISESSID',-value=>$session->id,-expires=>'2h');
    print "Set-Cookie: $cookie\n";
    print "Content-type: text/html\n\n";
    $array{stato}=1;
    $array{session}=$session;
    return %array;
  }
  #se sono qui la sessione non c'è. punto
  $array{descrizione}.=' : no submit form found';
  print "Content-type: text/html\n\n";
  return %array;
}

sub cambiaData {
#cambia il formato della data
  my $data=shift;
  my ($Td,$To)=split('T',$data);
  my ($Ta,$Tm,$Tg)=split('-',$Td);
  return "$To $Tg-$Tm-$Ta";
}

sub cambiaGet {
#cambia l'indirizzo in base alla presenza o assenza di ? nel get
  my $indirizzo=shift;
  if($indirizzo=~m/\?/) { return $indirizzo.'&amp;'; }
  return $indirizzo.'?'; 
}

sub operazioneCommento {
#segnala,rimuove o toglie la segnalazione ad un commento; cioè tutte le modifiche a xmlcommenti tranne l'inserimento che richiede molti più controlli
  my $param=shift;
  my $operazione=$param->{operazione};
  my $id=$param->{id};
  my $indirizzoxmlcommenti='../data/commenti.xml';
  my $admin; my $user; my $risultato;
  if(exists $param->{session}) {
    my $session=$param->{session};
    $user=$session->param('utente');
    $admin=$session->param('admin');
  }
  if(exists $param->{admin}) { $admin=$param->{admin}; }
  open (my $COMMENTI,"+< $indirizzoxmlcommenti");
  flock ($COMMENTI,2);
  my $xmlcommenti=XML::LibXML->new()->parse_file($indirizzoxmlcommenti);
  my $radicec=$xmlcommenti->getDocumentElement;
  
  if($radicec->exists("//commento[\@id=\'$id\']")) {
  #l'id corrisponde ad un commento presente nel file, posso farci delle operazioni
    my $nodocommento=$radicec->findnodes("//commento[\@id=\'$id\']")->get_node(1);
    my $utente=$nodocommento->findvalue('utente');
    if($nodocommento->hasAttribute('segnalato')) {
      if($operazione eq 'togli' and $admin eq 'true') {
	$nodocommento->removeAttribute('segnalato');
	$risultato='Commento tolto dalla lista dei segnalati';
      }
    } else {
      if($operazione eq 'segnala') {
	$nodocommento->setAttribute('segnalato', 'si');
	$risultato='Commento segnalato';
      }
    }
    if($operazione eq 'rimuovi' and ($admin eq 'true' or $user eq $utente)) {
      my $nodopadre=$nodocommento->parentNode;
      $nodopadre->removeChild($nodocommento);
      #se era l'unico commento elimino anche il nodo <ricetta>
      my $ricetta=$nodopadre->getAttribute('nome');
      unless($radicec->exists("//ricetta[\@nome=\'$ricetta\']/commento")) {
	my $nodoR=$radicec->findnodes("//ricetta[\@nome=\'$ricetta\']")->get_node(1);
	my $nodoP=$nodoR->parentNode;
	$nodoP->removeChild($nodoR);
      }
      $risultato='Commento rimosso';
    }
  }
  $xmlcommenti->toFile($indirizzoxmlcommenti);
  close (*COMMENTI); # si occupa lui di flock 8
  return $risultato;
}

1;
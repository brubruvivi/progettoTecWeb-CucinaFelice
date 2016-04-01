#!/usr/bin/perl -W
#registrazione.cgi
use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;
use CGI::Session;
use XML::LibXML;
use Fcntl qw(:flock :DEFAULT);

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#variabili usate nello script
my $indirizzo='registrazione.cgi';
my $indirizzoxmlutenti='../data/utenti.xml';
my $session; my $user;
my %registrazione;

#mi creo l'array hash con i dati di accesso dai valori passati tramite metodo post
read(STDIN,my $buffer,$ENV{'CONTENT_LENGTH'});
if($buffer) {
  my @pairs=split(/&/,$buffer);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/,$pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $registrazione{$name}=$value;
  }
}
#se arrivo tramite la form allora controllo i dati e li inserisco
if($registrazione{action} eq 'registrati') {
  #ricontrollo i dati per sicurezza (ripeto controlli lato client)
  #OBBLIGATORI
  if($registrazione{username}!~/[a-zA-Z0-9]{2,}/) { $registrazione{ERusername}=1; }#errore sull'username
  if($registrazione{password}!~/[a-zA-Z0-9]{8,20}/) { $registrazione{ERpassword}=1; }#errore sulla password
  if($registrazione{password} ne $registrazione{password2} ) { $registrazione{ERpassword2}=1; }#errore sul match delle password
  if($registrazione{email}!~/[a-zA-Z0-9_.+-]+\@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9_.+-]+/) { $registrazione{ERemail}=1; }#errore sull'email
  #OPZIONALI
  if($registrazione{nome}!~/\w+( \w+)*/) { $registrazione{ERnome}=1; }
  if($registrazione{cognome}!~/\w+( \w+)*/) { $registrazione{ERcognome}=1; }
  if($registrazione{abilita}!~/principiante|intermedia|professionista/) { $registrazione{ERabilita}=1; }
  if($registrazione{sesso}!~/M|F/) { $registrazione{ERsesso}=1; }
#eseguo i controlli sul database solo se i controlli sui campi obbligatori sono stati passati
  if(exists $registrazione{ERusername} or exists $registrazione{ERpassword} or exists $registrazione{ERpassword2} or exists $registrazione{ERemail}) {
    $registrazione{errore}='il javascript non sta facendo i controlli necessari, rispetta le regole se vuoi registrarti';
    stamp(%registrazione);
  }
#devo ricordarmi di non inserire i campi opzionali che avevano degli errori che il javascript non ha bloccato
  if(exists $registrazione{ERnome}) { delete $registrazione{nome}; }
  if(exists $registrazione{ERcognome}) { delete $registrazione{cognome}; }
  if(exists $registrazione{ERabilita}) { delete $registrazione{abilita}; }
  if(exists $registrazione{ERsesso}) { delete $registrazione{sesso}; }
#eseguo i controlli da effettuare lato server, cioè controlli sul database
  open(*UTENTI,"+< $indirizzoxmlutenti");
  flock(*UTENTI,2);
  my $xmlutenti=XML::LibXML->new()->parse_file($indirizzoxmlutenti);
  my $radiceu=$xmlutenti->getDocumentElement;
  if ($radiceu->exists("//username=\'$registrazione{username}\'")) {
    close(*UTENTI);
    $registrazione{errore}='l\'username è già utilizzato da un altro utente';
    stamp(%registrazione);
  }
  if($radiceu->exists("//email=\'$registrazione{email}\'")) {
    close(*UTENTI);
    $registrazione{errore}='l\'email è già stata usata per registrarsi';
    stamp(%registrazione);
  }
  #controlli terminati, modifico il file xml
  my $frammentoxmlutente='<utente admin="false"><username>'.$registrazione{username}.'</username><password>'.$registrazione{password}.'</password><email>'.$registrazione{email}.'</email><infoaggiuntive';
  if (exists $registrazione{sesso}) { $frammentoxmlutente.=' sesso="'.$registrazione{sesso}.'"'; }
  $frammentoxmlutente.='>';
  if (exists $registrazione{nome}) { $frammentoxmlutente.='<nome>'.$registrazione{nome}.'</nome>'; }
  if (exists $registrazione{cognome}) { $frammentoxmlutente.='<cognome>'.$registrazione{cognome}.'</cognome>'; }
  if (exists $registrazione{abilita}) { $frammentoxmlutente.='<abilita>'.$registrazione{abilita}.'</abilita>'; }
  $frammentoxmlutente.='</infoaggiuntive></utente>';
  my $nodoutente=XML::LibXML->new()->parse_balanced_chunk($frammentoxmlutente);
  my $nodopadre=$radiceu->findnodes('//utenti')->get_node(1);
  $nodopadre->appendChild($nodoutente);
  $xmlutenti->toFile($indirizzoxmlutenti);
  close(*UTENTI);
  #faccio il login dell'utente che si è appena registrato
  $session=CGI::Session->new();
  $session->expire('2h');
  $session->param('utente',$registrazione{username});
  $session->param('admin','false');
  if(exists $registrazione{abilita}) { $session->param('abilita',$registrazione{abilita}); }
  $user=$session->param('utente');
  my $cookie=CGI::Cookie->new(-name=>'CGISESSID',-value=>$session->id,-expires=>'2h');
  print "Set-Cookie: $cookie\n";
  print "Content-type: text/html\n\n";
  funzioni::printHead( {titolo=>'Registrazione'} );
  funzioni::printModuloLogin( {user=>$user} );
  funzioni::printPathNav( {dove=>'Registrazione'} );
  print '<p>Registrazione riuscita </p><a href="home.cgi">link alla home</a>';
  funzioni::printFoot( $indirizzo );
  exit;
}
# altrimenti carico la form; sono qui solo alla prima occorrenza dello script
stamp();

#fine
sub stamp {
#stampa la pagina di registrazione
  my %registrazione=$_[0];
  my %errform=$_[1];
  my $indirizzo='registrazione.cgi';
  print "Content-type: text/html\n\n";
  funzioni::printHead( {titolo=>'Registrazione'} );
  #printModuloLogin non lo metto
  funzioni::printPathNav( {dove=>'Registrazione'} );
  if(exists $registrazione{errore}) { print "<p>$registrazione{errore}</p>"; }
  print <<EOF;
<h1>Compila i campi per registrarti</h1>
<h2>I campi obbligatori sono contrassegnati da un asterisco (*)</h2>
<h3>L'username può contenere lettere maiuscole, minuscole e numeri, la password deve essere composta da minimo 8 caratteri, massimo 20 e deve contenere obbligatoriamente una lettera maiuscola, e un numero.</h3>
<form method="post" id="register" onsubmit="return controllatuz()" action="registrazione.cgi"><p>
<label class="left" for="username">Username*</label>
<input class="middle" type="text" name="username" onblur="controllauser()" id="username" value="$registrazione{username}" />
<span class="right" id="checkuser"></span></p><p> 
<label class="left" for="password1">Password*</label>
<input class="middle" type="password" name="password" onblur="controllapass()" id="password1" value="$registrazione{password}" />
<span class="right" id="checkpass"></span></p><p>
<label class="left" for="password2">Conferma password*</label>
<input class="middle" type="password" name="password2" onblur="controllapsw2()" id="password2" value="$registrazione{password2}" />
<span class="right" id="checkconf"></span></p><p>
<label class="left" for="email">E-mail*</label>
<input class="middle" type="text" name="email" id="email" onblur="controllamail()" value="$registrazione{email}" />
<span class="right" id="checkmail"></span></p><p>
<label class="left" for="nome">Nome</label>
<input class="middle" type="text" name="nome" id="nome" value="$registrazione{nome}" /></p><p>
<label class="left" for="cognome">Cognome</label>
<input class="middle" type="text" name="cognome" id="cognome" value="$registrazione{cognome}" /></p><p>
<label class="left" for="abilita">Abilità</label>
EOF

  print '<span class="right"><label for="principiante">Principiante </label><input type="radio" name="abilita" id="principiante" value="principiante"';
  if($registrazione{abilita} eq 'principiante') { print ' checked="checked"';  }
  print ' /><label class="justify" for="intermedia">Intermedia</label><input type="radio" name="abilita" id="intermedia" value="intermedia"';
  if($registrazione{abilita} eq 'intermedia') { print ' checked="checked"';  }
  print '/><label class="justify" for="professionista">Professionista</label><input type="radio" name="abilita" id="professionista" value="professionista"';
  if($registrazione{abilita} eq 'professionista') { print ' checked="checked"';  }
  print ' /></span></p><p><label class="left" for="sesso">Sesso</label><span class="right"><label for="male">Maschile </label><input type="radio" name="sesso" id="male" value="M"';
  if($registrazione{sesso} eq 'M') { print ' checked="checked"';  }
  print ' /><label class="justify" for="female">Femminile </label><input type="radio" name="sesso" id="female" value="F"';
  if($registrazione{sesso} eq 'F') { print ' checked="checked"';  }
  print ' /></span></p><p><input class="button" type="submit" name="action" value="registrati" /></p></form>';
  funzioni::printAncora;
  funzioni::printFoot( $indirizzo );
  exit;
}
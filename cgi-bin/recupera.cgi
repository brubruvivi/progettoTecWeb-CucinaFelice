#!/usr/bin/perl -W
#recupera.cgi
use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Session;
use XML::LibXML;
use Fcntl qw(:flock :DEFAULT);

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#inizializzazione variabili di controllo e delle strutture usate nello script
my $indirizzo='recupera.cgi';
my $indirizzoxmlutenti='../data/utenti.xml';
my %operazione; my $erroperazione;

#mi creo l'array hash con i dati di accesso dai valori passati tramite metodo post
read(STDIN,my $buffer,$ENV{'CONTENT_LENGTH'});
if($buffer) {
  my @pairs=split(/&/,$buffer);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/,$pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $operazione{$name}=$value;
  }
}
#recupero
if($operazione{action} eq 'recupera') {
  #controllo email
  if($operazione{email}!~/[a-zA-Z0-9_.+-]+\@[a-zA-Z0-9_.+-]+\.[a-zA-Z0-9_.+-]+/) {
    stamp($indirizzo,'emailE','pattern email sbagliato',$operazione{email});
  }
  open(*UTENTI,$indirizzoxmlutenti);
  flock(*UTENTI,1);
  my $xmlutenti=XML::LibXML->load_xml({IO=>*UTENTI});
  close(*UTENTI);
  my $radiceu=$xmlutenti->getDocumentElement;
  unless($radiceu->exists("//utente[email=\'$operazione{email}\']")) {
    stamp($indirizzo,'emailE','l\'email non è assocciata a nessun account',$operazione{email});
  }
  my $nodoutente=$radiceu->findnodes("//utente[email=\'$operazione{email}\']")->get_node(1);
  my $utente=$nodoutente->findvalue('username');
  my $password=$nodoutente->findvalue('password');
  stamp($indirizzo,'riuscito',$utente,$password);
}
stamp($indirizzo);

#fine
sub stamp {
  my $indirizzo=$_[0];
  my $stato=$_[1];
  my $username; my $password;
  my $errore; my $email;
  
  print "Content-type: text/html\n\n";
  funzioni::printHead( {titolo=>'Recupero'} );
  #non metto il modulo login
  funzioni::printPathNav( {dove=>'Recupero'} );
  if($stato eq 'riuscito') {
    $username=$_[2]; $password=$_[3];
    print "<div id=\"recupero\"><h2>Recupero avvenuto con successo</h2>";
    print "<p>La tua username è : $username</p>";
    print "<p>La tua password è : $password</p></div>";
  } else {
    if($stato eq 'emailE') { $errore=$_[2]; $email=$_[3]; }
    print "<div><h2>Qui puoi recuperare l'username e la password che hai dimenticato</h2><h3>È necessaria l'email</h3>";
    print '<form method="post" id="recupero" onsubmit="return controllarec()" action="recupera.cgi">';
    print '<p><label class="left" for="email">E-mail*</label><input class="middle" type="text" name="email" id="email" onblur="controllamail()" value="'.$email.'" /><span class="right" id="checkmail"></span></p>';
    if($stato eq 'emailE') { print "<p>$errore</p>"; }
    print '<p><input class="button" type="submit" name="action" value="recupera" /></p></form></div>';
  }
  funzioni::printFoot( $indirizzo );
  exit;
}
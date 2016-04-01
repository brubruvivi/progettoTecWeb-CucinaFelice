#!/usr/bin/perl -W
#home.cgi
use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Session;
use Fcntl qw(:flock :DEFAULT);

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#inizializzazione variabili di controllo e delle strutture usate nello script
my $indirizzo='home.cgi';
my $indirizzoxmlricette='../data/ricette.xml';
my $indirizzoxmlcommenti='../data/commenti.xml';
my $indirizzoxmlutenti='../data/utenti.xml';
my $session; my $user; my $admin; my %array;
my $stringaget; my %get;
my $fatto;

#controllo parametri metodo get
$stringaget=$ENV{'QUERY_STRING'};
if($stringaget) {
  my @pairs=split(/&/,$stringaget);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/, $pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $get{$name}=$value;
  }
}
#controllo sessione e vari
if($get{action} eq 'logout') { %array=funzioni::checkSession('logout'); }
else { %array=funzioni::checkSession; }
#caricamento dati se usiste la sezione
if($array{stato}) {
  $session=$array{session};
  $user=$session->param('utente');
  $admin=$session->param('admin');
}
#controllo se arrivo qui tramite il pulsante rimuovi commento
if(exists $get{rimuovi}) {
  my $id=$get{rimuovi};
  #rimuovo il commento con id=$id
  $fatto=funzioni::operazioneCommento( {operazione=>'rimuovi',id=>$id,session=>$session} );
}
#controllo se arrivo qui tramite il pulsante segnala commento
if(exists $get{segnala}) {
  my $id=$get{segnala};
  #segnalo il commento
  $fatto=funzioni::operazioneCommento( {operazione=>'segnala',id=>$id,session=>$session} );
}
if(exists $get{togli} and $admin eq 'true') {
  my $id=$get{togli};
  #tolgo la segnalazione del commento il commento
  $fatto=funzioni::operazioneCommento( {operazione=>'togli',id=>$id,admin=>'true'} );
}
#stampo l'html
funzioni::printHead({titolo=>'Home'});
if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
funzioni::printPathNav( {nascondi=>'home'} );

my $ricetta; my $nodoricetta;
#lista delle ultime ricette inserite
open(*RICETTE,$indirizzoxmlricette);
flock(*RICETTE,1);
my $xmlricette=XML::LibXML->load_xml({IO=>*RICETTE});
close(*RICETTE);
my $radicer=$xmlricette->getDocumentElement;
print '<div id="ricettenuove"><h1>lista delle ricette nuove</h1>';
for(my $cont=0; $cont<3;$cont++) {
  $nodoricetta=$radicer->findnodes("//ricetta[last()-$cont]")->get_node(1);
  my $nome=$nodoricetta->getAttribute('nome');
  my $nodoimmagine=$nodoricetta->findnodes('img')->get_node(1);
  my $linkricetta="ricetta.cgi?ricetta=$nome"; $linkricetta=~tr/ /+/;
  print '<div class="ricetta"><h2><a href="'.$linkricetta.'">'.$nome.'</a></h2><a href="'.$linkricetta.'">'.funzioni::previewImmagine( $nodoimmagine ).'</a></div>';
}
#lista degli ultimi commenti inseriti
print '</div><div id="commentirecenti"><h1>lista dei commenti recenti</h1>';
open(*COMMENTI,$indirizzoxmlcommenti);
flock(*COMMENTI,1);
my $xmlcommenti=XML::LibXML->load_xml({IO=>*COMMENTI});
close(*COMMENTI);
my $radicec=$xmlcommenti->getDocumentElement;
if($fatto) { print "<h2>$fatto</h2>"; }
#trovo i commenti
my $nCommenti=$radicec->getAttribute('n.commenti'); my $id; my @commentirecenti; my $i=0;
for(my $cont=0; $cont<3 and $nCommenti-($cont+$i)>0;$cont++) {
  my $id=$nCommenti-($cont+$i);
  if($radicec->exists("//commento[\@id=\'$id\']")) { push @commentirecenti,$radicec->findnodes("//commento[\@id=\'$id\']")->get_node(1); }
  else { $i++;$cont--; }
}
#stampo i commenti
while(scalar @commentirecenti) {
  my $nodocommento=shift @commentirecenti;
  $ricetta=$nodocommento->parentNode->getAttribute('nome');
  my $linkricetta="ricetta.cgi?ricetta=$ricetta"; $linkricetta=~tr/ /+/;
  print '<div><a href="'.$linkricetta.'">'.$ricetta.'</a>';
  funzioni::printCommento( {nodo=>$nodocommento,indirizzo=>$indirizzo,admin=>$admin,user=>$user} );
  print '</div>';
}
print '</div>';  
funzioni::printAncora;
funzioni::printFoot( $indirizzo );

#fine
#!/usr/bin/perl -W
#ricettario.cgi
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
my $indirizzo='ricettario.cgi';
my $indirizzoperl='ricettario.cgi';
my $indirizzoxmlricette='../data/ricette.xml';
my $session; my $user; my %array;
my $stringaget; my %get;
my $mostra;
my $difficolta; my $diff;

#controllo parametri metodo get
$stringaget=$ENV{'QUERY_STRING'};
if($stringaget) {
  my @pairs=split(/&/,$stringaget);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/,$pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $get{$name}=$value;
  }
}
#controllo sessione e vari
if($get{action} eq 'logout') { %array=funzioni::checkSession('logout'); }
else { %array=funzioni::checkSession; }
#caricamento dati se usiste la sessione
if($array{stato}) {
  $session=$array{session};
  $user=$session->param('utente');
}
#sottoinsieme del ricettario
if(exists $get{tipo}) { $mostra=$get{tipo}; }
if($mostra ne '' and $mostra ne 'aperitivi' and $mostra ne 'antipasti' and $mostra ne 'primi' and $mostra ne 'secondi' and $mostra ne 'contorni' and $mostra ne 'dolci') { $mostra=''; }
if($mostra ne '') { $indirizzo.="?tipo=$mostra"; }
#ricerca per difficoltà
if(exists $get {difficolta}) {
  $diff=1; $difficolta=$get{difficolta};
  if($difficolta ne 'bassa' and $difficolta ne 'media' and $difficolta ne 'alta') { $diff=''; }
  else { $indirizzo=funzioni::cambiaGet( $indirizzo )."difficolta=$difficolta"; }
}
#gestione delle pagine
open(*RICETTE,$indirizzoxmlricette);
flock(*RICETTE,1);
my $xmlricette=XML::LibXML->load_xml({IO=>*RICETTE});
close(*RICETTE);
my $radicer=$xmlricette->getDocumentElement;
my @nodi;
if($mostra) {
  if($diff) { @nodi=$radicer->findnodes("//ricetta[tipo=\'$mostra\' and difficolta=\'$difficolta\']"); }
  else { @nodi=$radicer->findnodes("//ricetta[tipo=\'$mostra\']"); }  
} else {
  if($diff) { @nodi=$radicer->findnodes("//ricetta[difficolta=\'$difficolta\']"); }
  else { @nodi=$radicer->getElementsByTagName('ricetta'); }
}
#ho le ricette da mostrare
my $nNodi= scalar @nodi;
my $nricette=4;
my $maxpage=int(($nNodi)/$nricette);
unless(int($nNodi%$nricette)) { $maxpage--; } #tolgo l'ultima pagina se vuota
my $page=0;
if(exists $get{page}) {$page=$get{page}; }
if($page and $page>$maxpage) { $page=$maxpage; }
if($page) { $indirizzo=funzioni::cambiaGet( $indirizzo )."page=$page"; }
#stampa l'html
funzioni::printHead( {titolo=>'Ricettario',keywords=>'ricettario'});
if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
if($mostra) { funzioni::printPathNav( {dove=>$mostra,nascondi=>$mostra} ); }
else { funzioni::printPathNav( {dove=>' Tutte le ricette',nascondi=>'all'} ); }
#stampo link per la difficoltà
print '<div id="difficolta"><h3>Cerca per difficoltà :</h3><ul><li>';
my $ind=$indirizzoperl;
if($page) { $ind=funzioni::cambiaGet( $ind )."page=$page"; } if($mostra) { $ind=funzioni::cambiaGet( $ind )."tipo=$mostra"; }
if($difficolta eq 'bassa') { print 'bassa'; }
else { print '<a href="'.funzioni::cambiaGet( $ind ).'difficolta=bassa">bassa</a>'; }
print '</li><li>';
if($difficolta eq 'media') { print 'media'; }
else { print '<a href="'.funzioni::cambiaGet( $ind ).'difficolta=media">media</a>'; }
print '</li><li>';
if($difficolta eq 'alta') { print 'alta'; }
else { print '<a href="'.funzioni::cambiaGet( $ind ).'difficolta=alta">alta</a>'; }
print '</li><li>';
unless($difficolta) { print 'tutte'; }
else {
  $ind=$indirizzoperl; if($mostra) { $ind=funzioni::cambiaGet( $ind )."tipo=$mostra"; }
  print '<a href="'.$ind.'">tutte</a>';
}
print '</li></ul></div>';
#se non c'è nessuna ricetta da mostrare
unless($nNodi) { noricette(); }
$ind=$indirizzoperl;
print '<div id="pagine">';
if($mostra) { $ind=funzioni::cambiaGet( $ind )."tipo=$mostra"; } if($difficolta) { $ind=funzioni::cambiaGet( $ind )."difficolta=$difficolta"; }
if($page) { print '<p><a href="'.funzioni::cambiaGet( $ind ).'page='.($page -1).'">pagina precedente</a></p>'; }
if($page<$maxpage) { print '<p><a href="'.funzioni::cambiaGet( $ind ).'page='.($page +1).'">pagina successiva</a></p>'; }
print '</div><div id="ricettario">';
#stampo le ricette
my $cont=0;
while($cont<$nricette and $page*$nricette+$cont<$nNodi) {
  my $ricetta=$nodi[$page*$nricette+$cont]; $cont++;
  my $nome=$ricetta->getAttribute('nome');
  my $tipo=$ricetta->findvalue('tipo');
  my $descrizione=$ricetta->findnodes('descrizione/text()')->get_node(1)->toString('UTF-8',1);
  my $linkricetta="ricetta.cgi?ricetta=$nome"; $linkricetta=~tr/ /+/;
  print '<div class="ricetta"><h2><a href="'.$linkricetta.'">'.$nome.'</a></h2>';
  my $urlimmagine=$ricetta->findnodes('img/url/text()')->get_node(1)->toString('UTF-8',1);
  print '<a class="immagine" href="'.$linkricetta.'"><img class="preview" src="../'.$urlimmagine.'" alt="immagine di presentazione della ricetta, clicca per andare alla pagina della ricetta" /></a><div class="testo">';
  unless($mostra){ print '<h3>'.$tipo.'</h3>'; }
  print '<p class="descrizione">'.$descrizione.'</p></div></div>';
}
print '<div id="pagine">';
if($mostra) { $ind=funzioni::cambiaGet( $ind )."tipo=$mostra"; } if($difficolta) { $ind=funzioni::cambiaGet( $ind )."difficolta=$difficolta"; }
if($page) { print '<p><a href="'.funzioni::cambiaGet( $ind ).'page='.($page -1).'">pagina precedente</a></p>'; }
if($page<$maxpage) { print '<p><a href="'.funzioni::cambiaGet( $ind ).'page='.($page +1).'">pagina successiva</a></p>'; }
print '</div></div>';
funzioni::printAncora;
funzioni::printFoot( $indirizzo );

#fine
sub noricette {
  print '<img class="preview" src="../immagini/no_ricette.jpg" alt="non ci sono ricette" /><p>Ops, Sembra proprio che non ci siano ricette</p>';
  funzioni::printFoot( $indirizzo );
  exit;
}
#!/usr/bin/perl -W
#ricetta.cgi
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use strict;
use warnings;
use diagnostics;
use XML::LibXML;
use Time::Piece;
use Fcntl qw(:flock :DEFAULT);

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#inizializzazione variabili di controllo e delle strutture usate nello script
my $indirizzoxmlricette='../data/ricette.xml';
my $indirizzoxmlcommenti='../data/commenti.xml';
my $session; my $user; my %array; my $admin; my $abil;
my %commento; my $fatto; my $commentato;
my $ricetta; my $nodoricetta;
my $stringaget; my %get;

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
  $ricetta=$get{ricetta};
}
#creo l'url
$ricetta=~tr/ /+/;
my $indirizzo="ricetta.cgi?ricetta=$ricetta";
$ricetta=~tr/+/ /;
#controllo sessione e vari
if($get{action} eq 'logout') { %array=funzioni::checkSession('logout'); }
else { %array=funzioni::checkSession; }
#caricamento dati se esiste la sezione
if($array{stato}) {
  $session=$array{session};
  $user=$session->param('utente');
  $admin=$session->param('admin');
  $abil=$session->param('abilita');
}
#devo avere una ricetta per questa pagina
unless($ricetta) {
#non so che ricetta cercare........
  funzioni::printHead({titolo=>'Ricetta'});
  if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
  else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
  funzioni::printPathNav( {nascondi=>'home',dove=>'ricetta'} );
  print '<h2>Nessuna ricetta selezionata, torna al <a href="ricettario.cgi">ricettario.</a> per scegliere una ricetta</h2>';
  funzioni::printFoot( $indirizzo );
  exit;
}
#cerco se esiste la ricetta nel file xml
open (*RICETTE,$indirizzoxmlricette);
flock(*RICETTE,1);
my $xmlricette=XML::LibXML->load_xml({IO=>*RICETTE});
close(*RICETTE);
my $radice=$xmlricette->getDocumentElement;
my $pathricetta="//ricetta[\@nome=\'$ricetta\']";
if($radice->exists($pathricetta)) { $nodoricetta=$radice->findnodes($pathricetta)->get_node(1); }
else {
  #non esiste la ricetta
  funzioni::printHead({titolo=>'Ricetta'});
  if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
  else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
  funzioni::printPathNav( {nascondi=>'home',dove=>'ricetta'} );
  print '<h2>Nessuna ricetta trovata che corrisponde a "'.$ricetta.'".';
  funzioni::printFoot( $indirizzo );
  exit;
  exit;
}
#ricetta presente nel database
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
#controllo se arrivo qui tramite il pulsante togli segnalazione
if(exists $get{togli} and $admin eq 'true') {
  my $id=$get{togli};
  #tolgo la segnalazione del commento il commento
  $fatto=funzioni::operazioneCommento( {operazione=>'togli',id=>$id,admin=>'true'} );
}
#controllo se arrivo qui tramite la form del commento
read(STDIN,my $buffer,$ENV{'CONTENT_LENGTH'});
if($buffer) {
  my @pairs=split(/&/,$buffer);
  foreach my $pair (@pairs) {
    my ($name,$value)=split(/=/, $pair);
    $value=~tr/+/ /; $value=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $name=~tr/+/ /; $name=~s/%([a-fA-F0-9][a-fA-F0-9])/pack("C",hex($1))/eg;
    $commento{$name}=$value;
  }
}
#inserimento del commento
if($array{stato} and $commento{action} eq 'commenta') {
#controllo i dati arrivati, devo essere loggato per inserire un commento
  # la ricetta lo ricavo dalla chiamata dello script
  # l'utente lo ricavo da $user
  if(exists $commento{testo} and $commento{testo} ne '') {
    #la data la ricavo da datetime
    if(exists $commento{voto} and $commento{voto}!~/^(1|2|3|4|5)$/){ delete $commento{voto}; } #se il voto è sbagliato lo elimino
    #inserisco il commento
    my $data=localtime->datetime;
    my $newxmlcommento="<testo>$commento{testo}</testo><data>$data</data></commento>";
    if(exists $commento{voto}) { $newxmlcommento="<voto>$commento{voto}</voto>".$newxmlcommento; }
    if($abil) { $newxmlcommento="<abilita>$abil</abilita>".$newxmlcommento; }
    $newxmlcommento="<commento><utente>$user</utente>".$newxmlcommento;
    my $nodo=XML::LibXML->new()->parse_balanced_chunk($newxmlcommento);
    open(*COMMENTI,"+< $indirizzoxmlcommenti");
    flock(*COMMENTI,2);
    my $xmlcommenti=XML::LibXML->new()->parse_file($indirizzoxmlcommenti);
    my $radicec=$xmlcommenti->getDocumentElement;
    #controllo se non ha inviato nuovamente il post del commento (es. ricaricando)
    unless($radicec->exists("//ricetta[\@nome=\'$ricetta\']/commento[utente=\'$user\' and testo=\"$commento{testo}\"]"))
    {
      my $id=$radicec->getAttribute('n.commenti')+1;
      $radicec->setAttribute('n.commenti', $id);
      $nodo->findnodes('//commento')->get_node(1)->setAttribute('id',$id);
      #cerco se esiste il nodoricetta o devo crearlo
      my $padrecommento;
      my $primocommento;
      if($xmlcommenti->exists("//ricetta[\@nome=\'$ricetta\']")) {
	$padrecommento=$xmlcommenti->findnodes("//ricetta[\@nome=\'$ricetta\']")->get_node(1);
	$primocommento=$xmlcommenti->findnodes("//ricetta[\@nome=\'$ricetta\']/commento")->get_node(1);
	$padrecommento->insertBefore($nodo,$primocommento);
      } else {
	$padrecommento=XML::LibXML::Element->new('ricetta');
	$padrecommento->appendChild($nodo);
	$padrecommento->setAttribute('nome',$ricetta);
	my $primonodo=$xmlcommenti->findnodes('//commenti')->get_node(1);
	$primonodo->appendChild($padrecommento);
      }
      $xmlcommenti->toFile($indirizzoxmlcommenti);
      close(*COMMENTI);
      $commentato=1;
    }
  }	
}
#stampo la pagina
my $tipo=$nodoricetta->findvalue('tipo');
my $dove='<a href="ricettario.cgi?tipo='.$tipo.'">'.ucfirst $tipo.'</a> &gt; '.$ricetta;

funzioni::printHead( {titolo=>$ricetta,keywords=>$ricetta} );
if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
funzioni::printPathNav( {dove=>$dove} );
my $nodoimmagine=$nodoricetta->findnodes('img')->get_node(1);
print '<div id="ricetta"><h1>'.$ricetta.'</h1>'.funzioni::previewImmagine( $nodoimmagine );
if($nodoricetta->exists('difficolta') or $nodoricetta->exists('tempo_preparazione')) {
  print '<div id="info">';
  if($nodoricetta->exists('difficolta')) {
    my $difficolta=$nodoricetta->findvalue('difficolta');
    print "<p>Questa ricetta ha una <em>difficolt&agrave; $difficolta</em></p>";
  }
  if($nodoricetta->exists('tempo_preparazione')) {
    my $tempo_preparazione=$nodoricetta->findvalue('tempo_preparazione');
    print "<p>Tempo di <em>preparazione : $tempo_preparazione minuti</em></p>";
  }
  print '</div>';
}
print '<div class="ingredienti"><span class="hide"><a href="#descrizione">Salta la lista di ingredienti</a></span>';
if($nodoricetta->exists('dosi_per')) {
  my $dosi_per=$nodoricetta->findvalue('dosi_per');
  print "<h3>Ingredienti per $dosi_per persone :</h3>"; }
else { print '<h3>Ingredienti :</h3>'; }
my $ingredienti=$nodoricetta->findnodes('ingredienti')->get_node(1)->toString('UTF-8',1);
$ingredienti=~s/<ingredienti>//g;
$ingredienti=~s/<\/ingredienti>//g;
$ingredienti=~s/<ingrediente>//g;
$ingredienti=~s/<\/ingrediente>//g;
$ingredienti=~s/,/<\/li><li>/g;
print '<ul><li>'.$ingredienti.'</li></ul></div><div id="descrizione"><h3>Descrizione</h3><p>';
my $descrizione=$nodoricetta->findnodes('descrizione/text()')->get_node(1)->toString('UTF-8',1);
print $descrizione.'</p></div><div id="procedimento"><h3>Procedimento</h3><p class="procedimento">';
my $procedimento=$nodoricetta->findnodes('procedimento')->get_node(1)->toString('UTF-8',1);
$procedimento=~s/<procedimento>//g;
$procedimento=~s/<\/procedimento>//g;
$procedimento=~s/<img><url>/<\/p><img class="IMG_procedimento" src="..\//g;
$procedimento=~s/<\/url><alt>/\" alt=\"/g;
$procedimento=~s/<\/alt><\/img>/\" \/><p class="procedimento">/g;
print $procedimento.'</p></div>';
print '</div><div id="commenti"><h2>Commenti</h2>';
#form commenti
if($array{stato}) {
  print '<form method="post" id="formcommento" action="'.$indirizzo.'">';
  print '<p id="voto">Voto</p><p id="voti"><label for="1">1</label><input type="radio" name="voto" id="1" value="1"';
  if(!$commentato and $commento{voto} eq '1') { print ' checked="checked"';  }
  print '/><label for="2">2</label><input type="radio" name="voto" id="2" value="2"';
  if(!$commentato and $commento{voto} eq '2') { print ' checked="checked"';  }
  print '/><label for="3">3</label><input type="radio" name="voto" id="3" value="3"';
  if(!$commentato and $commento{voto} eq '3') { print ' checked="checked"';  }
  print '/><label for="4">4</label><input type="radio" name="voto" id="4" value="4"';
  if(!$commentato and $commento{voto} eq '4') { print ' checked="checked"';  }
  print '/><label for="5">5</label><input type="radio" name="voto" id="5" value="5"';
  if(!$commentato and $commento{voto} eq '5') { print ' checked="checked"';  }
  print '/></p><p id="text"><label for="commenta">commenta</label><textarea name="testo" id="commenta" cols="60">';
  unless($commentato) { print $commento{testo}; }
  print '</textarea></p><p id="bottoni_form"><input type="submit" name="action" class="button" value="commenta"/></p></form>';
}
else { print '<p>Effettua il <a href="#login">login</a> oppure <a href="#register">registrati</a> per commentare</p>'; }
#preparo tutti i commenti della ricetta
print '<div id="listacommenti">';
open(*COMMENTI,$indirizzoxmlcommenti);
flock(*COMMENTI,1);
my $xmlcommenti=XML::LibXML->load_xml({IO=>*COMMENTI});
close(*COMMENTI);
if($xmlcommenti->exists("//ricetta[\@nome=\'$ricetta\']")) {
#ho almeno un commento da estrarre
  my @commenti=$xmlcommenti->findnodes("//ricetta[\@nome=\'$ricetta\']/commento");
  if($fatto) { print "<p>$fatto</p>"; }
  while(scalar @commenti) {
    my $nodocommento=shift @commenti;
    funzioni::printCommento( {nodo=>$nodocommento,user=>$user,admin=>$admin,indirizzo=>$indirizzo} );
  }
} else {
  print '<p>Nessuno ha commentato questa ricetta, fallo tu !</p>';
  if($fatto) { print "<p>$fatto</p>"; }
}
print '</div></div>';
funzioni::printAncora;
funzioni::printFoot( $indirizzo );

#fine
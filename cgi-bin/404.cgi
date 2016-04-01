#!/usr/bin/perl -W
#404.cgi
use strict;
use warnings;
use diagnostics;
use CGI;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Session;

use funzioni;

# script perl from ©The C-TEAM corporation
# ogni responsabilità NON è di Miki

#inizializzazione variabili di controllo e delle strutture usate nello script
my $indirizzo='404.cgi';
my $session; my $user; my %array;
my $stringaget; my %get;

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
}

funzioni::printHead({titolo=>'404'});
if($array{stato}) { funzioni::printModuloLogin( {user=>$user,indirizzo=>$indirizzo} ); }
else { funzioni::printModuloLogin( {indirizzo=>$indirizzo,errore=>$array{login},username=>$array{username},password=>$array{password}} ); }
funzioni::printPathNav( {nascondi=>'home',dove=>'404'} );
print '<h1>Pagina non trovata.</h1><h2>Siamo spiacenti la pagina non esiste, torna alla <span xml:lang="en">home page.</span></h2>';
funzioni::printFoot( $indirizzo );

#fine